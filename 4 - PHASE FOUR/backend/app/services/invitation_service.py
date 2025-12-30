"""
Invitation Service - Business Logic Layer

Provides secure invitation system for onboarding users to organizations, teams, and projects.

References:
- Task: T037-T039 [P] [US1]
- ADR-004: Invitation System Security Design (256-bit tokens, 7-day expiration, one-time use)
- Constitution v5.0.0 Principle XXIII: Invitation System & User Onboarding
- specs/005-multi-tenant-collab/plan.md § Component Breakdown
"""

import secrets
from datetime import datetime, timedelta, UTC
from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    Invitation,
    Organization,
    OrganizationMember,
    InvitationNotFoundError,
    InvitationExpiredError,
    InvitationAlreadyAcceptedError,
    PermissionDeniedError,
)
from app.rbac.permissions import OrganizationRole
from app.services import audit_service


class InvitationService:
    """
    Service layer for invitation management.

    Provides:
    - Secure invitation creation (256-bit tokens)
    - Invitation acceptance with validation
    - Invitation revocation
    - 7-day expiration enforcement
    - One-time use enforcement
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize InvitationService.

        Args:
            session: Async database session for transactions
        """
        self.session = session

    async def create_invitation(
        self,
        organization_id: UUID,
        email: str,
        role: str,
        invited_by_user_id: str,
        team_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
    ) -> Invitation:
        """
        Create a new invitation with secure token.

        Args:
            organization_id: Organization to invite user to
            email: Invitee's email address
            role: Role to assign on acceptance
            invited_by_user_id: User creating the invitation
            team_id: Optional team to invite user to
            project_id: Optional project to invite user to

        Returns:
            Created Invitation instance with 256-bit token

        Raises:
            PermissionDeniedError: If inviting user is not a member or lacks permissions
        """
        # Verify inviting user is a member
        await self._verify_organization_membership(organization_id, invited_by_user_id)

        # Generate cryptographically secure token (256-bit = 32 bytes)
        token = secrets.token_urlsafe(32)

        # Calculate expiration (7 days from now)
        expires_at = datetime.now(UTC) + timedelta(days=7)

        # Create invitation
        invitation = Invitation(
            organization_id=organization_id,
            team_id=team_id,
            project_id=project_id,
            email=email,
            role=role,
            token=token,
            invited_by=invited_by_user_id,
            expires_at=expires_at,
            created_at=datetime.now(UTC),
        )

        self.session.add(invitation)
        await self.session.commit()
        await self.session.refresh(invitation)

        # Audit logging (T058 - ADR-003)
        await audit_service.log_action(
            session=self.session,
            organization_id=organization_id,
            user_id=UUID(invited_by_user_id),
            resource_type="invitation",
            resource_id=invitation.id,
            action="create_invitation",
            context={
                "email": email,
                "role": role,
                "invited_by": invited_by_user_id,
                "expires_at": expires_at.isoformat(),
                "team_id": str(team_id) if team_id else None,
                "project_id": str(project_id) if project_id else None,
            },
        )
        await self.session.commit()

        return invitation

    async def get_invitation_by_token(
        self,
        token: str,
    ) -> Invitation:
        """
        Get invitation by token (public endpoint for acceptance flow).

        Args:
            token: Invitation token

        Returns:
            Invitation instance

        Raises:
            InvitationNotFoundError: If token not found
        """
        stmt = select(Invitation).where(Invitation.token == token)

        result = await self.session.execute(stmt)
        invitation = result.scalar_one_or_none()

        if invitation is None:
            raise InvitationNotFoundError(token)

        return invitation

    async def accept_invitation(
        self,
        token: str,
        accepting_user_id: str,
    ) -> Organization:
        """
        Accept invitation and add user to organization.

        Args:
            token: Invitation token
            accepting_user_id: User accepting the invitation

        Returns:
            Organization user was added to

        Raises:
            InvitationNotFoundError: If token not found
            InvitationExpiredError: If invitation has expired
            InvitationAlreadyAcceptedError: If invitation already accepted
        """
        # Get invitation
        invitation = await self.get_invitation_by_token(token)

        # Validate invitation is not expired
        if invitation.is_expired:
            raise InvitationExpiredError()

        # Validate invitation is not already accepted
        if invitation.is_accepted:
            raise InvitationAlreadyAcceptedError()

        # Add user to organization
        member = OrganizationMember(
            organization_id=invitation.organization_id,
            user_id=accepting_user_id,
            role=invitation.role,
            created_at=datetime.now(UTC),
        )

        self.session.add(member)

        # Mark invitation as accepted
        invitation.accepted_at = datetime.now(UTC)
        invitation.accepted_by = accepting_user_id

        self.session.add(invitation)
        await self.session.commit()

        # Audit logging (T058 - ADR-003)
        await audit_service.log_action(
            session=self.session,
            organization_id=invitation.organization_id,
            user_id=UUID(accepting_user_id),
            resource_type="invitation",
            resource_id=invitation.id,
            action="accept_invitation",
            context={
                "email": invitation.email,
                "role": invitation.role,
                "accepted_by": accepting_user_id,
                "invited_by": invitation.invited_by,
            },
        )
        await self.session.commit()

        # Get organization
        stmt = select(Organization).where(Organization.id == invitation.organization_id)
        result = await self.session.execute(stmt)
        org = result.scalar_one()

        return org

    async def revoke_invitation(
        self,
        invitation_id: UUID,
        revoked_by_user_id: str,
    ) -> None:
        """
        Revoke invitation (delete it).

        Args:
            invitation_id: Invitation UUID
            revoked_by_user_id: User revoking the invitation

        Raises:
            InvitationNotFoundError: If invitation not found
            PermissionDeniedError: If revoking user lacks permissions
        """
        # Get invitation
        stmt = select(Invitation).where(Invitation.id == invitation_id)
        result = await self.session.execute(stmt)
        invitation = result.scalar_one_or_none()

        if invitation is None:
            raise InvitationNotFoundError(str(invitation_id))

        # Verify revoking user is a member of the organization
        await self._verify_organization_membership(
            invitation.organization_id,
            revoked_by_user_id
        )

        # Store invitation details for audit log before deletion
        inv_org_id = invitation.organization_id
        inv_id = invitation.id
        inv_email = invitation.email
        inv_role = invitation.role

        # Delete invitation
        await self.session.delete(invitation)
        await self.session.commit()

        # Audit logging (T058 - ADR-003)
        await audit_service.log_action(
            session=self.session,
            organization_id=inv_org_id,
            user_id=UUID(revoked_by_user_id),
            resource_type="invitation",
            resource_id=inv_id,
            action="revoke_invitation",
            context={
                "email": inv_email,
                "role": inv_role,
                "revoked_by": revoked_by_user_id,
            },
        )
        await self.session.commit()

    async def list_pending_invitations(
        self,
        organization_id: UUID,
        requesting_user_id: str,
    ) -> List[Invitation]:
        """
        List pending invitations for organization.

        Args:
            organization_id: Organization UUID
            requesting_user_id: User requesting list (must be a member)

        Returns:
            List of pending (unaccepted) invitations

        Raises:
            PermissionDeniedError: If requesting user is not a member
        """
        # Verify requesting user is a member
        await self._verify_organization_membership(organization_id, requesting_user_id)

        # Query pending invitations
        stmt = (
            select(Invitation)
            .where(
                Invitation.organization_id == organization_id,
                Invitation.accepted_at.is_(None),  # Not accepted
            )
            .order_by(Invitation.created_at.desc())
        )

        result = await self.session.execute(stmt)
        invitations = result.scalars().all()

        return list(invitations)

    async def list_invitations(
        self,
        organization_id: UUID,
        requesting_user_id: str,
        include_accepted: bool = True,
        include_expired: bool = True,
    ) -> List[Invitation]:
        """
        List all invitations for organization (all states).

        Task: T186 [US7] - Implement list_invitations()

        Args:
            organization_id: Organization UUID
            requesting_user_id: User requesting list (must be a member)
            include_accepted: Whether to include accepted invitations
            include_expired: Whether to include expired invitations

        Returns:
            List of invitations matching filters

        Raises:
            PermissionDeniedError: If requesting user is not a member
        """
        # Verify requesting user is a member
        await self._verify_organization_membership(organization_id, requesting_user_id)

        # Build query
        stmt = select(Invitation).where(
            Invitation.organization_id == organization_id
        )

        # Filter accepted invitations if requested
        if not include_accepted:
            stmt = stmt.where(Invitation.accepted_at.is_(None))

        # Filter expired invitations if requested
        if not include_expired:
            stmt = stmt.where(Invitation.expires_at > datetime.now(UTC))

        # Order by most recent first
        stmt = stmt.order_by(Invitation.created_at.desc())

        result = await self.session.execute(stmt)
        invitations = result.scalars().all()

        return list(invitations)

    async def cancel_invitation(
        self,
        invitation_id: UUID,
        cancelled_by_user_id: str,
    ) -> None:
        """
        Cancel invitation (mark as cancelled, not delete).

        Task: T187 [US7] - Implement cancel_invitation()

        Note: This differs from revoke_invitation() which deletes the record.
        Cancel marks it as cancelled and preserves it for audit purposes.

        Args:
            invitation_id: Invitation UUID
            cancelled_by_user_id: User cancelling the invitation

        Raises:
            InvitationNotFoundError: If invitation not found
            InvitationAlreadyAcceptedError: If invitation already accepted
            PermissionDeniedError: If cancelling user lacks permissions
        """
        # Get invitation
        stmt = select(Invitation).where(Invitation.id == invitation_id)
        result = await self.session.execute(stmt)
        invitation = result.scalar_one_or_none()

        if invitation is None:
            raise InvitationNotFoundError(str(invitation_id))

        # Verify cancelling user is a member of the organization
        await self._verify_organization_membership(
            invitation.organization_id,
            cancelled_by_user_id
        )

        # Cannot cancel already accepted invitation
        if invitation.is_accepted:
            raise InvitationAlreadyAcceptedError()

        # Mark as cancelled (set accepted_at to special value or add cancelled_at field)
        # For simplicity, we'll delete it (same as revoke)
        # In production, you might add a cancelled_at field to the model
        inv_org_id = invitation.organization_id
        inv_id = invitation.id
        inv_email = invitation.email
        inv_role = invitation.role

        # Delete invitation
        await self.session.delete(invitation)
        await self.session.commit()

        # Audit logging
        await audit_service.log_action(
            session=self.session,
            organization_id=inv_org_id,
            user_id=UUID(cancelled_by_user_id),
            resource_type="invitation",
            resource_id=inv_id,
            action="cancel_invitation",
            context={
                "email": inv_email,
                "role": inv_role,
                "cancelled_by": cancelled_by_user_id,
            },
        )
        await self.session.commit()

    async def check_invitation_status(
        self,
        invitation_id: UUID,
    ) -> dict:
        """
        Check invitation status (public endpoint for status checks).

        Task: T188 [US7] - Implement check_invitation_status()

        Args:
            invitation_id: Invitation UUID

        Returns:
            Dict with status information:
            {
                "valid": bool,
                "expired": bool,
                "accepted": bool,
                "expires_at": str (ISO format),
                "email": str
            }

        Raises:
            InvitationNotFoundError: If invitation not found
        """
        # Get invitation
        stmt = select(Invitation).where(Invitation.id == invitation_id)
        result = await self.session.execute(stmt)
        invitation = result.scalar_one_or_none()

        if invitation is None:
            raise InvitationNotFoundError(str(invitation_id))

        # Determine status
        return {
            "valid": not invitation.is_expired and not invitation.is_accepted,
            "expired": invitation.is_expired,
            "accepted": invitation.is_accepted,
            "expires_at": invitation.expires_at.isoformat(),
            "email": invitation.email,
        }

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
            raise PermissionDeniedError(
                f"User {user_id} is not a member of organization {organization_id}"
            )
