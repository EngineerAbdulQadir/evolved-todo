"""
Organization Service - Business Logic Layer

Provides organization CRUD operations with tenant context validation and audit logging.

References:
- Task: T034-T036 [P] [US1]
- ADR-001: Multi-Tenant Data Isolation Strategy (application-level filtering)
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
    Organization,
    OrganizationMember,
    User,
    DuplicateSlugError,
    OrganizationNotFoundError,
    PermissionDeniedError,
)
from app.rbac.permissions import OrganizationRole
from app.services import audit_service


class OrganizationService:
    """
    Service layer for organization management.

    Provides:
    - Organization CRUD operations
    - Member management (add, remove, list)
    - Soft delete with 30-day recovery window
    - Permission validation for all operations
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize OrganizationService.

        Args:
            session: Async database session for transactions
        """
        self.session = session

    async def create_organization(
        self,
        name: str,
        slug: str,
        created_by_user_id: str,
        description: Optional[str] = None,
    ) -> Organization:
        """
        Create a new organization and add creator as OWNER.

        Args:
            name: Organization display name
            slug: URL-friendly unique identifier
            created_by_user_id: User ID of creator (will be added as owner)
            description: Optional organization description

        Returns:
            Created Organization instance

        Raises:
            DuplicateSlugError: If slug already exists
        """
        # Create organization
        org = Organization(
            name=name,
            slug=slug,
            description=description,
            created_at=datetime.now(UTC),
        )

        self.session.add(org)

        try:
            await self.session.flush()  # Check for unique constraint violation
        except IntegrityError as e:
            await self.session.rollback()
            if "slug" in str(e).lower():
                raise DuplicateSlugError(slug)
            raise

        # Add creator as owner
        member = OrganizationMember(
            organization_id=org.id,
            user_id=created_by_user_id,
            role=OrganizationRole.OWNER.value,
            created_at=datetime.now(UTC),
        )

        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(org)

        # Audit logging (T057 - ADR-003)
        # TODO: Fix user_id type mismatch (Better Auth uses string IDs, AuditLog expects UUID)
        # await audit_service.log_action(
        #     session=self.session,
        #     organization_id=org.id,
        #     user_id=created_by_user_id,
        #     resource_type="organization",
        #     resource_id=org.id,
        #     action="create",
        #     context={
        #         "name": org.name,
        #         "slug": org.slug,
        #         "description": org.description,
        #     },
        # )
        # await self.session.commit()

        return org

    async def get_organization(
        self,
        organization_id: UUID,
        user_id: str,
        include_deleted: bool = False,
    ) -> Organization:
        """
        Get organization by ID with membership validation.

        Args:
            organization_id: Organization UUID
            user_id: Requesting user ID (must be a member)
            include_deleted: Include soft-deleted organizations

        Returns:
            Organization instance

        Raises:
            OrganizationNotFoundError: If org not found or user not a member
        """
        # Verify user is a member
        await self._verify_membership(organization_id, user_id)

        # Query organization
        stmt = select(Organization).where(Organization.id == organization_id)

        if not include_deleted:
            stmt = stmt.where(Organization.deleted_at.is_(None))

        result = await self.session.execute(stmt)
        org = result.scalar_one_or_none()

        if org is None:
            raise OrganizationNotFoundError(str(organization_id))

        return org

    async def get_organization_by_slug(
        self,
        slug: str,
        user_id: str,
        include_deleted: bool = False,
    ) -> Organization:
        """
        Get organization by slug with membership validation.

        Args:
            slug: Organization slug
            user_id: Requesting user ID (must be a member)
            include_deleted: Include soft-deleted organizations

        Returns:
            Organization instance

        Raises:
            OrganizationNotFoundError: If org not found or user not a member
        """
        # Query organization
        stmt = select(Organization).where(Organization.slug == slug)

        if not include_deleted:
            stmt = stmt.where(Organization.deleted_at.is_(None))

        result = await self.session.execute(stmt)
        org = result.scalar_one_or_none()

        if org is None:
            raise OrganizationNotFoundError(slug)

        # Verify user is a member
        await self._verify_membership(org.id, user_id)

        return org

    async def list_organizations(
        self,
        user_id: str,
        include_deleted: bool = False,
    ) -> List[Organization]:
        """
        List organizations user is a member of.

        Args:
            user_id: Requesting user ID
            include_deleted: Include soft-deleted organizations

        Returns:
            List of organizations ordered by created_at DESC
        """
        # Query organizations through membership join
        stmt = (
            select(Organization)
            .join(OrganizationMember, Organization.id == OrganizationMember.organization_id)
            .where(OrganizationMember.user_id == user_id)
            .order_by(Organization.created_at.desc())
        )

        if not include_deleted:
            stmt = stmt.where(Organization.deleted_at.is_(None))

        result = await self.session.execute(stmt)
        orgs = result.scalars().all()

        return list(orgs)

    async def update_organization(
        self,
        organization_id: UUID,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        slug: Optional[str] = None,
    ) -> Organization:
        """
        Update organization details.

        Args:
            organization_id: Organization UUID
            user_id: Requesting user ID (must be owner or admin)
            name: New name (optional)
            description: New description (optional)
            slug: New slug (optional)

        Returns:
            Updated Organization instance

        Raises:
            OrganizationNotFoundError: If org not found
            PermissionDeniedError: If user lacks update permissions
            DuplicateSlugError: If new slug already exists
        """
        # Verify user has permission (owner or admin)
        role = await self._get_user_role(organization_id, user_id)

        if role not in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]:
            raise PermissionDeniedError("Only owners and admins can update organization")

        # Get organization
        org = await self.get_organization(organization_id, user_id)

        # Track changes for audit log (T057 - ADR-003)
        changes = {}

        # Update fields
        if name is not None and name != org.name:
            changes["name"] = {"before": org.name, "after": name}
            org.name = name

        if description is not None and description != org.description:
            changes["description"] = {"before": org.description, "after": description}
            org.description = description

        if slug is not None and slug != org.slug:
            changes["slug"] = {"before": org.slug, "after": slug}
            org.slug = slug

        self.session.add(org)

        try:
            await self.session.commit()
            await self.session.refresh(org)
        except IntegrityError as e:
            await self.session.rollback()
            if "slug" in str(e).lower() and slug:
                raise DuplicateSlugError(slug)
            raise

        # Audit logging (T057 - ADR-003)
        # TODO: Fix user_id type mismatch (Better Auth uses string IDs, AuditLog expects UUID)
        # if changes:
        #     await audit_service.log_action(
        #         session=self.session,
        #         organization_id=organization_id,
        #         user_id=user_id,
        #         resource_type="organization",
        #         resource_id=organization_id,
        #         action="update",
        #         context={"changes": changes},
        #     )
        #     await self.session.commit()

        return org

    async def soft_delete_organization(
        self,
        organization_id: UUID,
        deleted_by_user_id: str,
    ) -> None:
        """
        Soft delete organization (set deleted_at timestamp).

        Args:
            organization_id: Organization UUID
            deleted_by_user_id: User ID performing deletion (must be owner)

        Raises:
            OrganizationNotFoundError: If org not found
            PermissionDeniedError: If user is not owner
        """
        # Verify user is owner
        role = await self._get_user_role(organization_id, deleted_by_user_id)

        if role != OrganizationRole.OWNER.value:
            raise PermissionDeniedError("Only owners can delete organization")

        # Get organization
        org = await self.get_organization(organization_id, deleted_by_user_id)

        # Set deleted_at timestamp
        now = datetime.now(UTC)
        org.deleted_at = now

        self.session.add(org)
        await self.session.commit()

        # Audit logging (T057 - ADR-003)
        # TODO: Fix user_id type mismatch (Better Auth uses string IDs, AuditLog expects UUID)
        # from datetime import timedelta
        # recovery_until = now + timedelta(days=30)
        # await audit_service.log_action(
        #     session=self.session,
        #     organization_id=organization_id,
        #     user_id=deleted_by_user_id,
        #     resource_type="organization",
        #     resource_id=organization_id,
        #     action="soft_delete",
        #     context={
        #         "recovery_until": recovery_until.isoformat(),
        #         "organization_name": org.name,
        #         "organization_slug": org.slug,
        #     },
        # )
        # await self.session.commit()

    async def recover_organization(
        self,
        organization_id: UUID,
        recovered_by_user_id: str,
    ) -> Organization:
        """
        Recover soft-deleted organization (clear deleted_at timestamp).

        Task: T197 [US8] - Implement recover_organization()

        Args:
            organization_id: Organization UUID
            recovered_by_user_id: User ID performing recovery (must be owner)

        Returns:
            Recovered Organization instance

        Raises:
            OrganizationNotFoundError: If org not found
            PermissionDeniedError: If user is not owner or org not deleted
        """
        # Get organization (including deleted)
        org = await self.get_organization(
            organization_id, recovered_by_user_id, include_deleted=True
        )

        # Verify organization is actually deleted
        if org.deleted_at is None:
            raise PermissionDeniedError("Organization is not deleted")

        # Verify user is owner
        role = await self._get_user_role(organization_id, recovered_by_user_id)
        if role != OrganizationRole.OWNER.value:
            raise PermissionDeniedError("Only owners can recover organization")

        # Clear deleted_at timestamp
        org.deleted_at = None

        self.session.add(org)
        await self.session.commit()

        # Audit logging
        # TODO: Fix user_id type mismatch (Better Auth uses string IDs, AuditLog expects UUID)
        # await audit_service.log_action(
        #     session=self.session,
        #     organization_id=organization_id,
        #     user_id=recovered_by_user_id,
        #     resource_type="organization",
        #     resource_id=organization_id,
        #     action="recover",
        #     context={
        #         "organization_name": org.name,
        #         "organization_slug": org.slug,
        #         "recovered_by": recovered_by_user_id,
        #     },
        # )
        # await self.session.commit()

        return org

    async def add_member(
        self,
        organization_id: UUID,
        user_id: str,
        role: str,
        added_by_user_id: str,
    ) -> OrganizationMember:
        """
        Add member to organization.

        Args:
            organization_id: Organization UUID
            user_id: User ID to add
            role: Role to assign (owner, admin, member)
            added_by_user_id: User ID performing addition (must be owner or admin)

        Returns:
            Created OrganizationMember instance

        Raises:
            PermissionDeniedError: If adding user lacks permissions
        """
        # Verify adding user has permission
        adding_user_role = await self._get_user_role(organization_id, added_by_user_id)

        if adding_user_role not in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]:
            raise PermissionDeniedError("Only owners and admins can add members")

        # Create membership
        member = OrganizationMember(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
            created_at=datetime.now(UTC),
        )

        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)

        # Audit logging (T057 - ADR-003)
        # TODO: Fix user_id type mismatch (Better Auth uses string IDs, AuditLog expects UUID)
        # await audit_service.log_action(
        #     session=self.session,
        #     organization_id=organization_id,
        #     user_id=added_by_user_id,
        #     resource_type="organization_member",
        #     resource_id=member.id,
        #     action="add_member",
        #     context={
        #         "user_id": user_id,
        #         "role": role,
        #         "added_by": added_by_user_id,
        #     },
        # )
        # await self.session.commit()

        return member

    async def remove_member(
        self,
        organization_id: UUID,
        user_id: str,
        removed_by_user_id: str,
    ) -> None:
        """
        Remove member from organization.

        Args:
            organization_id: Organization UUID
            user_id: User ID to remove
            removed_by_user_id: User ID performing removal (must be owner or admin)

        Raises:
            PermissionDeniedError: If removing user lacks permissions
        """
        # Verify removing user has permission
        removing_user_role = await self._get_user_role(organization_id, removed_by_user_id)

        if removing_user_role not in [OrganizationRole.OWNER.value, OrganizationRole.ADMIN.value]:
            raise PermissionDeniedError("Only owners and admins can remove members")

        # Delete membership
        stmt = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )

        result = await self.session.execute(stmt)
        member = result.scalar_one_or_none()

        if member:
            # Store member details for audit log before deletion
            member_id = member.id
            member_role = member.role

            await self.session.delete(member)
            await self.session.commit()

            # Audit logging (T057 - ADR-003)
            # TODO: Fix user_id type mismatch (Better Auth uses string IDs, AuditLog expects UUID)
            # await audit_service.log_action(
            #     session=self.session,
            #     organization_id=organization_id,
            #     user_id=removed_by_user_id,
            #     resource_type="organization_member",
            #     resource_id=member_id,
            #     action="remove_member",
            #     context={
            #         "user_id": user_id,
            #         "role": member_role,
            #         "removed_by": removed_by_user_id,
            #     },
            # )
            # await self.session.commit()

    async def list_members(
        self,
        organization_id: UUID,
        requesting_user_id: str,
    ) -> List[OrganizationMember]:
        """
        List all members of organization.

        Args:
            organization_id: Organization UUID
            requesting_user_id: User ID requesting list (must be a member)

        Returns:
            List of OrganizationMember instances

        Raises:
            PermissionDeniedError: If requesting user is not a member
        """
        # Verify requesting user is a member
        await self._verify_membership(organization_id, requesting_user_id)

        # Query members
        stmt = (
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == organization_id)
            .order_by(OrganizationMember.created_at)
        )

        result = await self.session.execute(stmt)
        members = result.scalars().all()

        return list(members)

    # Private helper methods

    async def _verify_membership(
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

    async def _get_user_role(
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
            User's role (owner, admin, member)

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
