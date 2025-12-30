"""
Project Service - Business Logic Layer

Provides project CRUD operations with team scoping and RBAC enforcement.

References:
- Task: T101-T105 [US3]
- ADR-001: Multi-Tenant Data Isolation Strategy (application-level filtering)
- ADR-002: RBAC Middleware Architecture
- ADR-003: Soft Delete and Audit Trail Strategy
- Constitution v5.0.0 Principle XIX: Multi-Tenancy & Data Isolation Hierarchy
- specs/005-multi-tenant-collab/plan.md § Component Breakdown
"""

from datetime import datetime, UTC
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    Project,
    ProjectMember,
    Team,
    TeamMember,
    OrganizationMember,
    PermissionDeniedError,
)
from app.rbac.permissions import OrganizationRole, TeamRole, ProjectRole
from app.services import audit_service


class ProjectNotFoundError(Exception):
    """Raised when project is not found."""
    pass


class ProjectService:
    """
    Service layer for project management.

    Provides:
    - Project CRUD operations with team scoping
    - Member management (add, remove, list)
    - Soft delete with 30-day recovery window
    - RBAC enforcement (team lead can create projects, project manager can update)
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize ProjectService.

        Args:
            session: Async database session for transactions
        """
        self.session = session

    async def create_project(
        self,
        name: str,
        team_id: UUID,
        created_by_user_id: str,
        description: Optional[str] = None,
    ) -> Project:
        """
        Create a new project within a team.

        Args:
            name: Project display name
            team_id: Parent team UUID
            created_by_user_id: User ID of creator (must be team lead or org admin)
            description: Optional project description

        Returns:
            Created Project instance

        Raises:
            PermissionDeniedError: If user is not team lead or org admin
            IntegrityError: If project name already exists in team
            ValueError: If team not found

        Task: T101 [US3] - Validate team lead role, prevent duplicate names
        """
        # Get team and verify it exists
        team = await self._get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        # Verify user has permission (team lead or org admin/owner)
        has_permission = await self._has_team_lead_or_org_admin_permission(
            team.organization_id, team_id, created_by_user_id
        )
        if not has_permission:
            raise PermissionDeniedError(
                "Only team leads and organization admins can create projects"
            )

        # Check for duplicate project name within team
        existing_project = await self._get_project_by_name(team_id, name)
        if existing_project is not None:
            raise IntegrityError(
                statement=None,
                params=None,
                orig=Exception(f"Project name '{name}' already exists in team"),
            )

        # Create project
        project = Project(
            name=name,
            description=description,
            team_id=team_id,
            organization_id=team.organization_id,
            created_by=created_by_user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)

        # Audit logging (T128 - ADR-003)
        await audit_service.log_action(
            session=self.session,
            organization_id=team.organization_id,
            user_id=UUID(created_by_user_id),
            resource_type="project",
            resource_id=project.id,
            action="create",
            context={
                "name": project.name,
                "description": project.description,
                "team_id": str(team_id),
                "organization_id": str(team.organization_id),
            },
        )
        await self.session.commit()

        return project

    async def list_projects(
        self,
        team_id: UUID,
        user_id: str,
        include_deleted: bool = False,
    ) -> List[Project]:
        """
        List projects in team filtered by deleted_at.

        Args:
            team_id: Team UUID
            user_id: Requesting user ID (must be team member or org member)
            include_deleted: Include soft-deleted projects

        Returns:
            List of Project instances ordered by created_at DESC

        Raises:
            PermissionDeniedError: If user is not team member or org member

        Task: T102 [US3] - Filter by team_id + deleted_at IS NULL
        """
        # Get team to verify existence and get organization_id
        team = await self._get_team(team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")

        # Verify user is team member or organization member
        is_org_member = await self._is_organization_member(team.organization_id, user_id)
        if not is_org_member:
            raise PermissionDeniedError(
                f"User {user_id} is not a member of organization {team.organization_id}"
            )

        # Query projects with team scoping
        query = select(Project).where(Project.team_id == team_id)

        if not include_deleted:
            query = query.where(Project.deleted_at.is_(None))

        query = query.order_by(Project.created_at.desc())

        result = await self.session.execute(query)
        projects = result.scalars().all()

        return list(projects)

    async def get_project(
        self,
        project_id: UUID,
        user_id: str,
        include_deleted: bool = False,
    ) -> Project:
        """
        Get project by ID with membership validation.

        Args:
            project_id: Project UUID
            user_id: Requesting user ID
            include_deleted: Include soft-deleted projects

        Returns:
            Project instance

        Raises:
            ProjectNotFoundError: If project not found
            PermissionDeniedError: If user not authorized

        Task: T103 [US3] - Validate project membership or org membership
        """
        query = select(Project).where(Project.id == project_id)

        if not include_deleted:
            query = query.where(Project.deleted_at.is_(None))

        result = await self.session.execute(query)
        project = result.scalar_one_or_none()

        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        # Verify user is organization member (team/project membership inherited)
        is_org_member = await self._is_organization_member(project.organization_id, user_id)
        if not is_org_member:
            raise PermissionDeniedError(
                f"User {user_id} is not authorized to access project {project_id}"
            )

        return project

    async def update_project(
        self,
        project_id: UUID,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Project:
        """
        Update project details.

        Args:
            project_id: Project UUID
            user_id: Requesting user ID (must be project manager or team lead or org admin)
            name: New project name (optional)
            description: New project description (optional)

        Returns:
            Updated Project instance

        Raises:
            ProjectNotFoundError: If project not found
            PermissionDeniedError: If user lacks permission

        Task: T104 [US3] - Require project manager role
        """
        project = await self.get_project(project_id, user_id)

        # Verify user has permission (project manager, team lead, or org admin)
        project_role = await self._get_project_role(project_id, user_id)
        team_role = await self._get_team_role(project.team_id, user_id)
        org_role = await self._get_organization_role(project.organization_id, user_id)

        # Allow: project manager, team lead, org admin/owner
        is_project_manager = project_role == ProjectRole.MANAGER.value
        is_team_lead = team_role == TeamRole.LEAD.value
        is_org_admin = org_role in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]

        if not (is_project_manager or is_team_lead or is_org_admin):
            raise PermissionDeniedError(
                "Only project managers, team leads, and org admins can update projects"
            )

        # Store old values for audit
        old_name = project.name
        old_description = project.description

        # Update fields
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description

        project.updated_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(project)

        # Audit logging (T128 - ADR-003)
        await audit_service.log_action(
            session=self.session,
            organization_id=project.organization_id,
            user_id=UUID(user_id),
            resource_type="project",
            resource_id=project.id,
            action="update",
            context={
                "before": {"name": old_name, "description": old_description},
                "after": {"name": project.name, "description": project.description},
            },
        )
        await self.session.commit()

        return project

    async def delete_project(
        self,
        project_id: UUID,
        deleted_by_user_id: str,
    ) -> None:
        """
        Soft delete project (30-day recovery window).

        Args:
            project_id: Project UUID
            deleted_by_user_id: User ID performing deletion

        Raises:
            ProjectNotFoundError: If project not found
            PermissionDeniedError: If user lacks permission

        Task: T105 [US3] - Soft delete with cascading to tasks
        """
        project = await self.get_project(project_id, deleted_by_user_id)

        # Verify user has permission (project manager, team lead, or org admin)
        project_role = await self._get_project_role(project_id, deleted_by_user_id)
        team_role = await self._get_team_role(project.team_id, deleted_by_user_id)
        org_role = await self._get_organization_role(project.organization_id, deleted_by_user_id)

        is_project_manager = project_role == ProjectRole.MANAGER.value
        is_team_lead = team_role == TeamRole.LEAD.value
        is_org_admin = org_role in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]

        if not (is_project_manager or is_team_lead or is_org_admin):
            raise PermissionDeniedError(
                "Only project managers, team leads, and org admins can delete projects"
            )

        # Soft delete project
        project.deleted_at = datetime.now(UTC)

        # Cascade soft delete to tasks (ADR-003)
        from app.models import Task
        query = select(Task).where(
            Task.project_id == project_id,
            Task.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        tasks = result.scalars().all()

        for task in tasks:
            task.deleted_at = datetime.now(UTC)

        await self.session.commit()

        # Audit logging (T128 - ADR-003)
        await audit_service.log_action(
            session=self.session,
            organization_id=project.organization_id,
            user_id=UUID(deleted_by_user_id),
            resource_type="project",
            resource_id=project.id,
            action="delete",
            context={
                "name": project.name,
                "team_id": str(project.team_id),
                "cascaded_tasks": len(tasks),
            },
        )
        await self.session.commit()

    async def recover_project(
        self,
        project_id: UUID,
        recovered_by_user_id: str,
    ) -> Project:
        """
        Recover soft-deleted project (clear deleted_at timestamp).

        Task: T199 [US8] - Implement recover_project()

        Args:
            project_id: Project UUID
            recovered_by_user_id: User ID performing recovery

        Returns:
            Recovered Project instance

        Raises:
            ProjectNotFoundError: If project not found
            PermissionDeniedError: If user lacks recovery permissions or project not deleted
        """
        # Get project (including deleted)
        stmt = select(Project).where(Project.id == project_id)
        result = await self.session.execute(stmt)
        project = result.scalar_one_or_none()

        if project is None:
            raise ProjectNotFoundError(project_id)

        # Verify project is actually deleted
        if project.deleted_at is None:
            raise PermissionDeniedError("Project is not deleted")

        # Verify user has permission (project manager, team lead, or org admin)
        project_role = await self._get_project_role(project_id, recovered_by_user_id)
        team_role = await self._get_team_role(project.team_id, recovered_by_user_id)
        org_role = await self._get_organization_role(project.organization_id, recovered_by_user_id)

        is_project_manager = project_role == ProjectRole.MANAGER.value
        is_team_lead = team_role == TeamRole.LEAD.value
        is_org_admin = org_role in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]

        if not (is_project_manager or is_team_lead or is_org_admin):
            raise PermissionDeniedError(
                "Only project managers, team leads, and org admins can recover projects"
            )

        # Clear deleted_at timestamp
        project.deleted_at = None
        project.updated_at = datetime.now(UTC)

        # Cascade recovery to tasks
        from app.models import Task
        query = select(Task).where(
            Task.project_id == project_id,
            Task.deleted_at.is_not(None)
        )
        result = await self.session.execute(query)
        tasks = result.scalars().all()

        for task in tasks:
            task.deleted_at = None

        await self.session.commit()
        await self.session.refresh(project)

        # Audit logging
        await audit_service.log_action(
            session=self.session,
            organization_id=project.organization_id,
            user_id=UUID(recovered_by_user_id),
            resource_type="project",
            resource_id=project.id,
            action="recover",
            context={
                "name": project.name,
                "team_id": str(project.team_id),
                "recovered_tasks": len(tasks),
                "recovered_by": recovered_by_user_id,
            },
        )
        await self.session.commit()

        return project

    # Helper methods

    async def _get_team(self, team_id: UUID) -> Optional[Team]:
        """Get team by ID."""
        query = select(Team).where(Team.id == team_id, Team.deleted_at.is_(None))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_project_by_name(self, team_id: UUID, name: str) -> Optional[Project]:
        """Get project by name within team (including deleted)."""
        query = select(Project).where(
            Project.team_id == team_id,
            Project.name == name,
            Project.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _is_organization_member(self, organization_id: UUID, user_id: str) -> bool:
        """Check if user is organization member."""
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
        result = await self.session.execute(query)
        member = result.scalar_one_or_none()
        return member is not None

    async def _get_organization_role(self, organization_id: UUID, user_id: str) -> Optional[str]:
        """Get user's organization role."""
        query = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
        result = await self.session.execute(query)
        member = result.scalar_one_or_none()
        return member.role if member else None

    async def _get_team_role(self, team_id: UUID, user_id: str) -> Optional[str]:
        """Get user's team role."""
        query = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )
        result = await self.session.execute(query)
        member = result.scalar_one_or_none()
        return member.role if member else None

    async def _get_project_role(self, project_id: UUID, user_id: str) -> Optional[str]:
        """Get user's project role."""
        query = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        result = await self.session.execute(query)
        member = result.scalar_one_or_none()
        return member.role if member else None

    async def _has_team_lead_or_org_admin_permission(
        self, organization_id: UUID, team_id: UUID, user_id: str
    ) -> bool:
        """Check if user is team lead or organization admin/owner."""
        org_role = await self._get_organization_role(organization_id, user_id)
        if org_role in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]:
            return True

        team_role = await self._get_team_role(team_id, user_id)
        if team_role == TeamRole.LEAD.value:
            return True

        return False
