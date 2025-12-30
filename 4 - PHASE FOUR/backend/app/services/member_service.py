"""
Member Service - Business Logic Layer

Provides member management for organizations, teams, and projects.

References:
- Task: T076-T077 [US2], T106-T107 [US3]
- ADR-002: RBAC Middleware Architecture
- ADR-003: Soft Delete and Audit Trail Strategy
- Constitution v5.0.0 Principle XX: Role-Based Access Control
- specs/005-multi-tenant-collab/plan.md § Component Breakdown
"""

from datetime import datetime, UTC
from typing import List
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    OrganizationMember,
    TeamMember,
    ProjectMember,
    Team,
    Project,
    PermissionDeniedError,
    TeamNotFoundError,
)
from app.rbac.permissions import OrganizationRole, TeamRole, ProjectRole
from app.services import audit_service


class ProjectNotFoundError(Exception):
    """Raised when project is not found."""
    pass


class MemberService:
    """
    Service layer for member management across organization, team, and project levels.

    Provides:
    - Add/remove members from teams
    - List team members
    - RBAC enforcement (org admin or team lead can add/remove members)
    - Validation (user must be org member before joining team)
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize MemberService.

        Args:
            session: Async database session for transactions
        """
        self.session = session

    async def add_team_member(
        self,
        team_id: UUID,
        user_id: str,
        role: str,
        added_by_user_id: str,
    ) -> TeamMember:
        """
        Add member to team with role assignment.

        Args:
            team_id: Team UUID
            user_id: User ID to add to team
            role: Team role to assign (lead, member)
            added_by_user_id: User ID performing addition (must be team lead or org admin)

        Returns:
            Created TeamMember instance

        Raises:
            TeamNotFoundError: If team not found
            PermissionDeniedError: If adding user lacks permissions or user not org member
            IntegrityError: If user already a team member

        Task: T076 [US2] - Validate org membership first
        """
        # Get team
        team = await self._get_team(team_id)

        # Verify adding user has permission (team lead or org admin)
        has_permission = await self._has_team_lead_or_org_admin_permission(
            team.organization_id,
            team_id,
            added_by_user_id,
        )

        if not has_permission:
            raise PermissionDeniedError("Only team leads and organization admins can add team members")

        # Validate target user is organization member (REQUIRED)
        is_org_member = await self._is_organization_member(team.organization_id, user_id)
        if not is_org_member:
            raise PermissionDeniedError(
                f"User {user_id} must be an organization member before joining team"
            )

        # Check if already a team member
        existing_member = await self._get_team_member(team_id, user_id)
        if existing_member is not None:
            raise IntegrityError(
                statement=None,
                params=None,
                orig=Exception(f"User {user_id} is already a member of team {team_id}"),
            )

        # Create team membership
        member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role=role,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)

        # Audit logging (T089 - ADR-003)
        await audit_service.log_action(
            session=self.session,
            organization_id=team.organization_id,
            user_id=UUID(added_by_user_id),
            resource_type="team_member",
            resource_id=member.id,
            action="add_member",
            context={
                "team_id": str(team_id),
                "user_id": user_id,
                "role": role,
                "added_by": added_by_user_id,
            },
        )
        await self.session.commit()

        return member

    async def remove_team_member(
        self,
        team_id: UUID,
        user_id: str,
        removed_by_user_id: str,
    ) -> None:
        """
        Remove member from team.

        Args:
            team_id: Team UUID
            user_id: User ID to remove from team
            removed_by_user_id: User ID performing removal (must be team lead or org admin)

        Raises:
            TeamNotFoundError: If team not found
            PermissionDeniedError: If removing user lacks permissions

        Task: T077 [US2] - Remove team membership
        """
        # Get team
        team = await self._get_team(team_id)

        # Verify removing user has permission (team lead or org admin)
        has_permission = await self._has_team_lead_or_org_admin_permission(
            team.organization_id,
            team_id,
            removed_by_user_id,
        )

        if not has_permission:
            raise PermissionDeniedError("Only team leads and organization admins can remove team members")

        # Get team member
        stmt = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )

        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if member:
            # Store member details for audit log before deletion
            member_id = member.id
            member_role = member.role

            await self.session.delete(member)
            await self.session.commit()

            # Audit logging (T089 - ADR-003)
            await audit_service.log_action(
                session=self.session,
                organization_id=team.organization_id,
                user_id=UUID(removed_by_user_id),
                resource_type="team_member",
                resource_id=member_id,
                action="remove_member",
                context={
                    "team_id": str(team_id),
                    "user_id": user_id,
                    "role": member_role,
                    "removed_by": removed_by_user_id,
                },
            )
            await self.session.commit()

    async def list_team_members(
        self,
        team_id: UUID,
        requesting_user_id: str,
    ) -> List[TeamMember]:
        """
        List all members of team.

        Args:
            team_id: Team UUID
            requesting_user_id: User ID requesting list (must be org member)

        Returns:
            List of TeamMember instances ordered by created_at

        Raises:
            TeamNotFoundError: If team not found
            PermissionDeniedError: If requesting user is not org member
        """
        # Get team
        team = await self._get_team(team_id)

        # Verify requesting user is organization member
        await self._verify_organization_membership(team.organization_id, requesting_user_id)

        # Query team members
        stmt = (
            select(TeamMember)
            .where(TeamMember.team_id == team_id)
            .order_by(TeamMember.created_at)
        )

        result = await self.session.execute(stmt)
        members = result.scalars().all()

        return list(members)

    async def add_project_member(
        self,
        project_id: UUID,
        user_id: str,
        role: str,
        added_by_user_id: str,
    ) -> ProjectMember:
        """
        Add member to project with role assignment.

        Args:
            project_id: Project UUID
            user_id: User ID to add to project
            role: Project role to assign (manager, contributor, viewer)
            added_by_user_id: User ID performing addition (must be project manager or team lead or org admin)

        Returns:
            Created ProjectMember instance

        Raises:
            ProjectNotFoundError: If project not found
            PermissionDeniedError: If adding user lacks permissions or user not team member
            IntegrityError: If user already a project member

        Task: T106 [US3] - Validate team membership first
        """
        # Get project
        project = await self._get_project(project_id)

        # Verify adding user has permission (project manager, team lead, or org admin)
        has_permission = await self._has_project_manager_or_team_lead_or_org_admin_permission(
            project.organization_id,
            project.team_id,
            project_id,
            added_by_user_id,
        )

        if not has_permission:
            raise PermissionDeniedError(
                "Only project managers, team leads, and organization admins can add project members"
            )

        # Validate target user is team member (REQUIRED)
        is_team_member = await self._is_team_member(project.team_id, user_id)
        if not is_team_member:
            raise PermissionDeniedError(
                f"User {user_id} must be a team member before joining project"
            )

        # Check if already a project member
        existing_member = await self._get_project_member(project_id, user_id)
        if existing_member is not None:
            raise IntegrityError(
                statement=None,
                params=None,
                orig=Exception(f"User {user_id} is already a member of project {project_id}"),
            )

        # Create project membership
        member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            role=role,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)

        # Audit logging (T129 - ADR-003)
        await audit_service.log_action(
            session=self.session,
            organization_id=project.organization_id,
            user_id=UUID(added_by_user_id),
            resource_type="project_member",
            resource_id=member.id,
            action="add_member",
            context={
                "project_id": str(project_id),
                "team_id": str(project.team_id),
                "user_id": user_id,
                "role": role,
                "added_by": added_by_user_id,
            },
        )
        await self.session.commit()

        return member

    async def remove_project_member(
        self,
        project_id: UUID,
        user_id: str,
        removed_by_user_id: str,
    ) -> None:
        """
        Remove member from project.

        Args:
            project_id: Project UUID
            user_id: User ID to remove from project
            removed_by_user_id: User ID performing removal (must be project manager or team lead or org admin)

        Raises:
            ProjectNotFoundError: If project not found
            PermissionDeniedError: If removing user lacks permissions

        Task: T107 [US3] - Remove project membership
        """
        # Get project
        project = await self._get_project(project_id)

        # Verify removing user has permission (project manager, team lead, or org admin)
        has_permission = await self._has_project_manager_or_team_lead_or_org_admin_permission(
            project.organization_id,
            project.team_id,
            project_id,
            removed_by_user_id,
        )

        if not has_permission:
            raise PermissionDeniedError(
                "Only project managers, team leads, and organization admins can remove project members"
            )

        # Get project member
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )

        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if member:
            # Store member details for audit log before deletion
            member_id = member.id
            member_role = member.role

            await self.session.delete(member)
            await self.session.commit()

            # Audit logging (T129 - ADR-003)
            await audit_service.log_action(
                session=self.session,
                organization_id=project.organization_id,
                user_id=UUID(removed_by_user_id),
                resource_type="project_member",
                resource_id=member_id,
                action="remove_member",
                context={
                    "project_id": str(project_id),
                    "team_id": str(project.team_id),
                    "user_id": user_id,
                    "role": member_role,
                    "removed_by": removed_by_user_id,
                },
            )
            await self.session.commit()

    async def list_project_members(
        self,
        project_id: UUID,
        requesting_user_id: str,
    ) -> List[ProjectMember]:
        """
        List all members of project.

        Args:
            project_id: Project UUID
            requesting_user_id: User ID requesting list (must be org member)

        Returns:
            List of ProjectMember instances ordered by created_at

        Raises:
            ProjectNotFoundError: If project not found
            PermissionDeniedError: If requesting user is not org member
        """
        # Get project
        project = await self._get_project(project_id)

        # Verify requesting user is organization member
        await self._verify_organization_membership(project.organization_id, requesting_user_id)

        # Query project members
        stmt = (
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .order_by(ProjectMember.created_at)
        )

        result = await self.session.execute(stmt)
        members = result.scalars().all()

        return list(members)

    # Private helper methods

    async def _get_team(self, team_id: UUID) -> Team:
        """
        Get team by ID.

        Args:
            team_id: Team UUID

        Returns:
            Team instance

        Raises:
            TeamNotFoundError: If team not found or soft-deleted
        """
        stmt = select(Team).where(
            Team.id == team_id,
            Team.deleted_at.is_(None),
        )

        result = await self.session.execute(stmt)
        team = result.scalar_one_or_none()

        if team is None:
            raise TeamNotFoundError(str(team_id))

        return team

    async def _is_organization_member(
        self,
        organization_id: UUID,
        user_id: str,
    ) -> bool:
        """
        Check if user is organization member.

        Args:
            organization_id: Organization UUID
            user_id: User ID

        Returns:
            True if user is organization member, False otherwise
        """
        stmt = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )

        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        return member is not None

    async def _verify_organization_membership(
        self,
        organization_id: UUID,
        user_id: str,
    ) -> None:
        """
        Verify user is organization member.

        Args:
            organization_id: Organization UUID
            user_id: User ID

        Raises:
            PermissionDeniedError: If user is not organization member
        """
        is_member = await self._is_organization_member(organization_id, user_id)
        if not is_member:
            raise PermissionDeniedError(
                f"User {user_id} is not a member of organization {organization_id}"
            )

    async def _get_organization_role(
        self,
        organization_id: UUID,
        user_id: str,
    ) -> str:
        """
        Get user's role in organization.

        Args:
            organization_id: Organization UUID
            user_id: User ID

        Returns:
            User's organization role (owner, admin, member)

        Raises:
            PermissionDeniedError: If user is not a member
        """
        stmt = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )

        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if member is None:
            raise PermissionDeniedError(
                f"User {user_id} is not a member of organization {organization_id}"
            )

        return member.role

    async def _get_team_role(
        self,
        team_id: UUID,
        user_id: str,
    ) -> str | None:
        """
        Get user's role in team (if member).

        Args:
            team_id: Team UUID
            user_id: User ID

        Returns:
            User's team role (lead, member) or None if not a member
        """
        member = await self._get_team_member(team_id, user_id)
        return member.role if member else None

    async def _get_team_member(
        self,
        team_id: UUID,
        user_id: str,
    ) -> TeamMember | None:
        """
        Get team member by team_id and user_id.

        Args:
            team_id: Team UUID
            user_id: User ID

        Returns:
            TeamMember instance or None if not found
        """
        stmt = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _has_team_lead_or_org_admin_permission(
        self,
        organization_id: UUID,
        team_id: UUID,
        user_id: str,
    ) -> bool:
        """
        Check if user has team lead or org admin permission.

        Args:
            organization_id: Organization UUID
            team_id: Team UUID
            user_id: User ID

        Returns:
            True if user is team lead or org admin/owner, False otherwise
        """
        # Check organization role
        org_role = await self._get_organization_role(organization_id, user_id)
        if org_role in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]:
            return True

        # Check team role
        team_role = await self._get_team_role(team_id, user_id)
        if team_role == TeamRole.LEAD.value:
            return True

        return False

    async def _get_project(self, project_id: UUID) -> Project:
        """
        Get project by ID.

        Args:
            project_id: Project UUID

        Returns:
            Project instance

        Raises:
            ProjectNotFoundError: If project not found or soft-deleted
        """
        stmt = select(Project).where(
            Project.id == project_id,
            Project.deleted_at.is_(None),
        )

        result = await self.session.execute(stmt)
        project = result.scalar_one_or_none()

        if project is None:
            raise ProjectNotFoundError(str(project_id))

        return project

    async def _is_team_member(
        self,
        team_id: UUID,
        user_id: str,
    ) -> bool:
        """
        Check if user is team member.

        Args:
            team_id: Team UUID
            user_id: User ID

        Returns:
            True if user is team member, False otherwise
        """
        member = await self._get_team_member(team_id, user_id)
        return member is not None

    async def _get_project_member(
        self,
        project_id: UUID,
        user_id: str,
    ) -> ProjectMember | None:
        """
        Get project member by project_id and user_id.

        Args:
            project_id: Project UUID
            user_id: User ID

        Returns:
            ProjectMember instance or None if not found
        """
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_project_role(
        self,
        project_id: UUID,
        user_id: str,
    ) -> str | None:
        """
        Get user's role in project (if member).

        Args:
            project_id: Project UUID
            user_id: User ID

        Returns:
            User's project role (manager, contributor, viewer) or None if not a member
        """
        member = await self._get_project_member(project_id, user_id)
        return member.role if member else None

    async def _has_project_manager_or_team_lead_or_org_admin_permission(
        self,
        organization_id: UUID,
        team_id: UUID,
        project_id: UUID,
        user_id: str,
    ) -> bool:
        """
        Check if user has project manager or team lead or org admin permission.

        Args:
            organization_id: Organization UUID
            team_id: Team UUID
            project_id: Project UUID
            user_id: User ID

        Returns:
            True if user is project manager or team lead or org admin/owner, False otherwise
        """
        # Check organization role
        org_role = await self._get_organization_role(organization_id, user_id)
        if org_role in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]:
            return True

        # Check team role
        team_role = await self._get_team_role(team_id, user_id)
        if team_role == TeamRole.LEAD.value:
            return True

        # Check project role
        project_role = await self._get_project_role(project_id, user_id)
        if project_role == ProjectRole.MANAGER.value:
            return True

        return False
