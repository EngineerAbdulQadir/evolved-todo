"""
Team Service - Business Logic Layer

Provides team CRUD operations with organization scoping and RBAC enforcement.

References:
- Task: T071-T075 [US2]
- ADR-001: Multi-Tenant Data Isolation Strategy (application-level filtering)
- ADR-002: RBAC Middleware Architecture
- ADR-003: Soft Delete and Audit Trail Strategy
- Constitution v5.0.0 Principle XIX: Multi-Tenancy & Data Isolation Hierarchy
- specs/005-multi-tenant-collab/plan.md § Component Breakdown
"""

from datetime import datetime, UTC, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    Team,
    TeamMember,
    OrganizationMember,
    TeamNotFoundError,
    PermissionDeniedError,
)
from app.rbac.permissions import OrganizationRole, TeamRole
from app.services import audit_service


class TeamService:
    """
    Service layer for team management.

    Provides:
    - Team CRUD operations with organization scoping
    - Member management (add, remove, list)
    - Soft delete with 30-day recovery window
    - RBAC enforcement (org admin can create teams, team lead can update)
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize TeamService.

        Args:
            session: Async database session for transactions
        """
        self.session = session

    async def create_team(
        self,
        name: str,
        organization_id: UUID,
        created_by_user_id: str,
        description: Optional[str] = None,
    ) -> Team:
        """
        Create a new team within an organization.

        Args:
            name: Team display name
            organization_id: Parent organization UUID
            created_by_user_id: User ID of creator (must be org admin or owner)
            description: Optional team description

        Returns:
            Created Team instance

        Raises:
            PermissionDeniedError: If user is not org admin or owner
            IntegrityError: If team name already exists in organization

        Task: T071 [US2] - Validate org admin role, prevent duplicate names
        """
        # Verify user has permission (org admin or owner)
        org_role = await self._get_organization_role(organization_id, created_by_user_id)

        if org_role not in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]:
            raise PermissionDeniedError("Only organization owners and admins can create teams")

        # Check for duplicate team name within organization
        existing_team = await self._get_team_by_name(organization_id, name)
        if existing_team is not None:
            raise IntegrityError(
                statement=None,
                params=None,
                orig=Exception(f"Team name '{name}' already exists in organization"),
            )

        # Create team
        team = Team(
            name=name,
            description=description,
            organization_id=organization_id,
            created_by=created_by_user_id,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        self.session.add(team)
        await self.session.commit()
        await self.session.refresh(team)

        # Audit logging (T089 - ADR-003)
        await audit_service.log_action(
            session=self.session,
            organization_id=organization_id,
            user_id=UUID(created_by_user_id),
            resource_type="team",
            resource_id=team.id,
            action="create",
            context={
                "name": team.name,
                "description": team.description,
                "organization_id": str(organization_id),
            },
        )
        await self.session.commit()

        return team

    async def list_teams(
        self,
        organization_id: UUID,
        user_id: str,
        include_deleted: bool = False,
    ) -> List[Team]:
        """
        List teams in organization filtered by deleted_at.

        Args:
            organization_id: Organization UUID
            user_id: Requesting user ID (must be org member)
            include_deleted: Include soft-deleted teams

        Returns:
            List of Team instances ordered by created_at DESC

        Raises:
            PermissionDeniedError: If user is not organization member

        Task: T072 [US2] - Filter by organization_id + deleted_at IS NULL
        """
        # Verify user is organization member
        await self._verify_organization_membership(organization_id, user_id)

        # Query teams
        stmt = (
            select(Team)
            .where(Team.organization_id == organization_id)
            .order_by(Team.created_at.desc())
        )

        if not include_deleted:
            stmt = stmt.where(Team.deleted_at.is_(None))

        result = await self.session.execute(stmt)
        teams = result.scalars().all()

        return list(teams)

    async def get_team(
        self,
        team_id: UUID,
        user_id: str,
        include_deleted: bool = False,
    ) -> Team:
        """
        Get team by ID with membership validation.

        Args:
            team_id: Team UUID
            user_id: Requesting user ID (must be team member or org admin)
            include_deleted: Include soft-deleted teams

        Returns:
            Team instance

        Raises:
            TeamNotFoundError: If team not found or user lacks access

        Task: T073 [US2] - Validate team membership
        """
        # Query team
        stmt = select(Team).where(Team.id == team_id)

        if not include_deleted:
            stmt = stmt.where(Team.deleted_at.is_(None))

        result = await self.session.execute(stmt)
        team = result.scalar_one_or_none()

        if team is None:
            raise TeamNotFoundError(str(team_id))

        # Verify user has access (org member is sufficient for viewing)
        await self._verify_organization_membership(team.organization_id, user_id)

        return team

    async def update_team(
        self,
        team_id: UUID,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Team:
        """
        Update team details.

        Args:
            team_id: Team UUID
            user_id: Requesting user ID (must be team lead or org admin)
            name: New name (optional)
            description: New description (optional)

        Returns:
            Updated Team instance

        Raises:
            TeamNotFoundError: If team not found
            PermissionDeniedError: If user lacks update permissions

        Task: T074 [US2] - Require team lead role
        """
        # Get team
        team = await self.get_team(team_id, user_id)

        # Verify user has permission (team lead or org admin)
        has_permission = await self._has_team_lead_or_org_admin_permission(
            team.organization_id,
            team_id,
            user_id,
        )

        if not has_permission:
            raise PermissionDeniedError("Only team leads and organization admins can update team")

        # Track changes for audit log (T089 - ADR-003)
        changes = {}

        # Update fields
        if name is not None and name != team.name:
            # Check for duplicate name
            existing_team = await self._get_team_by_name(team.organization_id, name)
            if existing_team is not None and existing_team.id != team_id:
                raise IntegrityError(
                    statement=None,
                    params=None,
                    orig=Exception(f"Team name '{name}' already exists in organization"),
                )

            changes["name"] = {"before": team.name, "after": name}
            team.name = name

        if description is not None and description != team.description:
            changes["description"] = {"before": team.description, "after": description}
            team.description = description

        if changes:
            team.updated_at = datetime.now(UTC)
            self.session.add(team)
            await self.session.commit()
            await self.session.refresh(team)

            # Audit logging (T089 - ADR-003)
            await audit_service.log_action(
                session=self.session,
                organization_id=team.organization_id,
                user_id=UUID(user_id),
                resource_type="team",
                resource_id=team_id,
                action="update",
                context={"changes": changes},
            )
            await self.session.commit()

        return team

    async def delete_team(
        self,
        team_id: UUID,
        deleted_by_user_id: str,
    ) -> None:
        """
        Soft delete team (set deleted_at timestamp).

        Cascades soft delete to all projects and tasks within the team.

        Args:
            team_id: Team UUID
            deleted_by_user_id: User ID performing deletion (must be team lead or org admin)

        Raises:
            TeamNotFoundError: If team not found
            PermissionDeniedError: If user lacks delete permissions

        Task: T075 [US2] - Soft delete with cascade to projects/tasks
        """
        # Get team
        team = await self.get_team(team_id, deleted_by_user_id)

        # Verify user has permission (team lead or org admin)
        has_permission = await self._has_team_lead_or_org_admin_permission(
            team.organization_id,
            team_id,
            deleted_by_user_id,
        )

        if not has_permission:
            raise PermissionDeniedError("Only team leads and organization admins can delete team")

        # Set deleted_at timestamp
        now = datetime.now(UTC)
        team.deleted_at = now
        team.updated_at = now

        self.session.add(team)
        await self.session.commit()

        # TODO: Cascade soft delete to projects and tasks (will be implemented in User Story 3)

        # Audit logging (T089 - ADR-003)
        recovery_until = now + timedelta(days=30)
        await audit_service.log_action(
            session=self.session,
            organization_id=team.organization_id,
            user_id=UUID(deleted_by_user_id),
            resource_type="team",
            resource_id=team_id,
            action="soft_delete",
            context={
                "recovery_until": recovery_until.isoformat(),
                "team_name": team.name,
                "organization_id": str(team.organization_id),
            },
        )
        await self.session.commit()

    async def recover_team(
        self,
        team_id: UUID,
        recovered_by_user_id: str,
    ) -> Team:
        """
        Recover soft-deleted team (clear deleted_at timestamp).

        Task: T198 [US8] - Implement recover_team()

        Args:
            team_id: Team UUID
            recovered_by_user_id: User ID performing recovery (must be team lead or org admin)

        Returns:
            Recovered Team instance

        Raises:
            TeamNotFoundError: If team not found
            PermissionDeniedError: If user lacks recovery permissions or team not deleted
        """
        # Get team (including deleted)
        stmt = select(Team).where(Team.id == team_id)
        result = await self.session.execute(stmt)
        team = result.scalar_one_or_none()

        if team is None:
            raise TeamNotFoundError(team_id)

        # Verify team is actually deleted
        if team.deleted_at is None:
            raise PermissionDeniedError("Team is not deleted")

        # Verify user has permission (team lead or org admin)
        has_permission = await self._has_team_lead_or_org_admin_permission(
            team.organization_id,
            team_id,
            recovered_by_user_id,
        )

        if not has_permission:
            raise PermissionDeniedError("Only team leads and organization admins can recover team")

        # Clear deleted_at timestamp
        team.deleted_at = None
        team.updated_at = datetime.now(UTC)

        self.session.add(team)
        await self.session.commit()
        await self.session.refresh(team)

        # Audit logging
        await audit_service.log_action(
            session=self.session,
            organization_id=team.organization_id,
            user_id=UUID(recovered_by_user_id),
            resource_type="team",
            resource_id=team_id,
            action="recover",
            context={
                "team_name": team.name,
                "organization_id": str(team.organization_id),
                "recovered_by": recovered_by_user_id,
            },
        )
        await self.session.commit()

        return team

    # Private helper methods

    async def _verify_organization_membership(
        self,
        organization_id: UUID,
        user_id: str,
    ) -> None:
        """
        Verify user is a member of organization.

        Args:
            organization_id: Organization UUID
            user_id: User ID to verify

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
            raise PermissionDeniedError(f"User {user_id} is not a member of organization {organization_id}")

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
            raise PermissionDeniedError(f"User {user_id} is not a member of organization {organization_id}")

        return member.role

    async def _get_team_role(
        self,
        team_id: UUID,
        user_id: str,
    ) -> Optional[str]:
        """
        Get user's role in team (if member).

        Args:
            team_id: Team UUID
            user_id: User ID

        Returns:
            User's team role (lead, member) or None if not a member
        """
        stmt = select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
        )

        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        return member.role if member else None

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

    async def _get_team_by_name(
        self,
        organization_id: UUID,
        name: str,
    ) -> Optional[Team]:
        """
        Get team by name within organization.

        Args:
            organization_id: Organization UUID
            name: Team name

        Returns:
            Team instance or None if not found
        """
        stmt = select(Team).where(
            Team.organization_id == organization_id,
            Team.name == name,
            Team.deleted_at.is_(None),
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
