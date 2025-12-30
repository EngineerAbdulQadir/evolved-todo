"""
Invitation Service Unit Tests

Tests for InvitationService business logic including token generation,
expiration, and acceptance workflows.

References:
- Task: T028 [P] [US1]
- Spec: specs/005-multi-tenant-collab/spec.md §2.1.2 (Invitation System)
- Constitution v5.0.0 Principle XXIII: Invitation System & User Onboarding
- ADR-004: Invitation System Security Design
"""

import pytest
import secrets
from datetime import datetime, timedelta, UTC
from uuid import uuid4, UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Organization, OrganizationMember, User, Invitation
from app.services.invitation_service import InvitationService
from app.services.organization_service import OrganizationService
from app.models.exceptions import (
    InvitationNotFoundError,
    InvitationExpiredError,
    InvitationAlreadyAcceptedError,
    PermissionDeniedError,
)


@pytest.mark.asyncio
class TestInvitationService:
    """
    Unit tests for InvitationService.

    Covers:
    - Invitation creation with 256-bit token
    - Invitation expiration (7 days)
    - Invitation acceptance (one-time use)
    - Invitation revocation
    - Permission checks for invitation management
    """

    async def test_create_invitation_success(
        self, session: AsyncSession, test_org: Organization, test_user: User
    ):
        """
        Test successful invitation creation.

        Expected:
        - Invitation created with valid UUID
        - Token is 256-bit cryptographically secure (urlsafe)
        - Expiration is 7 days from creation
        - Status is pending (accepted_at is None)
        """
        # Arrange
        invitation_service = InvitationService(session)

        # Act
        invitation = await invitation_service.create_invitation(
            organization_id=test_org.id,
            email="newuser@example.com",
            role="member",
            invited_by_user_id=test_user.id
        )

        # Assert invitation properties
        assert invitation.id is not None
        assert isinstance(invitation.id, UUID)
        assert invitation.organization_id == test_org.id
        assert invitation.email == "newuser@example.com"
        assert invitation.role == "member"
        assert invitation.invited_by == test_user.id

        # Assert token is cryptographically secure (256-bit = 32 bytes = ~43 urlsafe chars)
        assert len(invitation.token) >= 40
        assert invitation.token.replace("-", "").replace("_", "").isalnum()

        # Assert expiration is 7 days from now
        expected_expiration = datetime.now(UTC) + timedelta(days=7)
        time_diff = abs((invitation.expires_at - expected_expiration).total_seconds())
        assert time_diff < 5, "Expiration should be approximately 7 days from now"

        # Assert invitation is pending
        assert invitation.accepted_at is None
        assert invitation.accepted_by is None
        assert invitation.is_accepted is False
        assert invitation.is_expired is False

    async def test_create_invitation_with_team(
        self, session: AsyncSession, test_org: Organization, test_user: User
    ):
        """
        Test creating invitation with team assignment.

        Expected: Invitation includes team_id for automatic team membership on acceptance
        """
        # Arrange
        invitation_service = InvitationService(session)
        team_id = uuid4()

        # Act
        invitation = await invitation_service.create_invitation(
            organization_id=test_org.id,
            team_id=team_id,
            email="teamuser@example.com",
            role="member",
            invited_by_user_id=test_user.id
        )

        # Assert
        assert invitation.team_id == team_id

    async def test_create_invitation_permission_denied(
        self, session: AsyncSession, test_org: Organization, other_user: User
    ):
        """
        Test that non-members cannot create invitations.

        Expected: PermissionDeniedError raised for non-members
        """
        # Arrange
        invitation_service = InvitationService(session)

        # Act & Assert: Other user (not a member) attempts to invite
        with pytest.raises(PermissionDeniedError):
            await invitation_service.create_invitation(
                organization_id=test_org.id,
                email="hacker@example.com",
                role="owner",  # Attempting to invite as owner
                invited_by_user_id=other_user.id  # Not a member
            )

    async def test_get_invitation_by_token(
        self, session: AsyncSession, test_org: Organization, test_user: User
    ):
        """
        Test retrieving invitation by token.

        Expected: Invitation retrieved successfully using token
        """
        # Arrange
        invitation_service = InvitationService(session)

        created_invitation = await invitation_service.create_invitation(
            organization_id=test_org.id,
            email="lookup@example.com",
            role="member",
            invited_by_user_id=test_user.id
        )

        # Act
        retrieved_invitation = await invitation_service.get_invitation_by_token(
            token=created_invitation.token
        )

        # Assert
        assert retrieved_invitation.id == created_invitation.id
        assert retrieved_invitation.token == created_invitation.token

    async def test_get_invitation_not_found(
        self, session: AsyncSession
    ):
        """
        Test retrieving non-existent invitation.

        Expected: InvitationNotFoundError raised
        """
        # Arrange
        invitation_service = InvitationService(session)
        fake_token = secrets.token_urlsafe(32)

        # Act & Assert
        with pytest.raises(InvitationNotFoundError):
            await invitation_service.get_invitation_by_token(token=fake_token)

    async def test_accept_invitation_success(
        self, session: AsyncSession, test_org: Organization, test_user: User, other_user: User
    ):
        """
        Test successful invitation acceptance.

        Expected:
        - Invitation marked as accepted
        - User added to organization with specified role
        - accepted_at and accepted_by fields populated
        """
        # Arrange
        invitation_service = InvitationService(session)
        org_service = OrganizationService(session)

        invitation = await invitation_service.create_invitation(
            organization_id=test_org.id,
            email=other_user.email,
            role="member",
            invited_by_user_id=test_user.id
        )

        # Act
        await invitation_service.accept_invitation(
            token=invitation.token,
            accepting_user_id=other_user.id
        )

        # Assert: Invitation marked as accepted
        accepted_invitation = await invitation_service.get_invitation_by_token(
            token=invitation.token
        )

        assert accepted_invitation.is_accepted is True
        assert accepted_invitation.accepted_at is not None
        assert accepted_invitation.accepted_by == other_user.id

        # Assert: User added to organization
        members = await org_service.list_members(
            organization_id=test_org.id,
            requesting_user_id=test_user.id
        )

        member_ids = {member.user_id for member in members}
        assert other_user.id in member_ids

        # Find the new member and check role
        new_member = next(m for m in members if m.user_id == other_user.id)
        assert new_member.role == "member"

    async def test_accept_invitation_expired(
        self, session: AsyncSession, test_org: Organization, test_user: User, other_user: User
    ):
        """
        Test accepting expired invitation.

        Expected: InvitationExpiredError raised
        """
        # Arrange
        invitation_service = InvitationService(session)

        invitation = await invitation_service.create_invitation(
            organization_id=test_org.id,
            email=other_user.email,
            role="member",
            invited_by_user_id=test_user.id
        )

        # Manually expire the invitation
        invitation.expires_at = datetime.now(UTC) - timedelta(days=1)
        session.add(invitation)
        await session.commit()

        # Act & Assert
        with pytest.raises(InvitationExpiredError):
            await invitation_service.accept_invitation(
                token=invitation.token,
                accepting_user_id=other_user.id
            )

    async def test_accept_invitation_already_accepted(
        self, session: AsyncSession, test_org: Organization, test_user: User, other_user: User
    ):
        """
        Test accepting invitation that was already accepted (one-time use).

        Expected: InvitationAlreadyAcceptedError raised
        """
        # Arrange
        invitation_service = InvitationService(session)

        invitation = await invitation_service.create_invitation(
            organization_id=test_org.id,
            email=other_user.email,
            role="member",
            invited_by_user_id=test_user.id
        )

        # First acceptance (should succeed)
        await invitation_service.accept_invitation(
            token=invitation.token,
            accepting_user_id=other_user.id
        )

        # Act & Assert: Second acceptance (should fail)
        with pytest.raises(InvitationAlreadyAcceptedError):
            await invitation_service.accept_invitation(
                token=invitation.token,
                accepting_user_id=other_user.id
            )

    async def test_revoke_invitation(
        self, session: AsyncSession, test_org: Organization, test_user: User
    ):
        """
        Test revoking invitation.

        Expected:
        - Invitation is deleted or marked as revoked
        - Cannot be accepted after revocation
        """
        # Arrange
        invitation_service = InvitationService(session)

        invitation = await invitation_service.create_invitation(
            organization_id=test_org.id,
            email="revoked@example.com",
            role="member",
            invited_by_user_id=test_user.id
        )

        # Act
        await invitation_service.revoke_invitation(
            invitation_id=invitation.id,
            revoked_by_user_id=test_user.id
        )

        # Assert: Invitation no longer retrievable
        with pytest.raises(InvitationNotFoundError):
            await invitation_service.get_invitation_by_token(token=invitation.token)

    async def test_list_pending_invitations_for_organization(
        self, session: AsyncSession, test_org: Organization, test_user: User, other_user: User
    ):
        """
        Test listing pending invitations for an organization.

        Expected:
        - Only pending (unaccepted) invitations returned
        - Accepted invitations excluded
        - Expired invitations excluded by default
        """
        # Arrange
        invitation_service = InvitationService(session)

        # Create pending invitation
        pending_inv = await invitation_service.create_invitation(
            organization_id=test_org.id,
            email="pending@example.com",
            role="member",
            invited_by_user_id=test_user.id
        )

        # Create and accept invitation
        accepted_inv = await invitation_service.create_invitation(
            organization_id=test_org.id,
            email=other_user.email,
            role="member",
            invited_by_user_id=test_user.id
        )
        await invitation_service.accept_invitation(
            token=accepted_inv.token,
            accepting_user_id=other_user.id
        )

        # Act
        pending_invitations = await invitation_service.list_pending_invitations(
            organization_id=test_org.id,
            requesting_user_id=test_user.id
        )

        # Assert: Only pending invitation returned
        assert len(pending_invitations) == 1
        assert pending_invitations[0].id == pending_inv.id
        assert pending_invitations[0].is_accepted is False

    async def test_invitation_token_uniqueness(
        self, session: AsyncSession, test_org: Organization, test_user: User
    ):
        """
        Test that invitation tokens are unique.

        Expected: Each invitation has a unique token (no collisions)
        """
        # Arrange
        invitation_service = InvitationService(session)

        # Act: Create multiple invitations
        tokens = set()
        for i in range(100):
            invitation = await invitation_service.create_invitation(
                organization_id=test_org.id,
                email=f"user{i}@example.com",
                role="member",
                invited_by_user_id=test_user.id
            )
            tokens.add(invitation.token)

        # Assert: All tokens are unique
        assert len(tokens) == 100, "Token collision detected!"


@pytest.fixture
async def test_org(session: AsyncSession, test_user: User) -> Organization:
    """Create a test organization for invitation tests."""
    org_service = OrganizationService(session)

    org = await org_service.create_organization(
        name="Test Organization",
        slug="test-org",
        created_by_user_id=test_user.id
    )

    return org


@pytest.fixture
async def test_user(session: AsyncSession) -> User:
    """Create a test user (organization owner) for invitation tests."""
    user = User(
        id="owner@example.com",
        email="owner@example.com",
        name="Test Owner",
        email_verified=True,
        created_at=datetime.now(UTC),
    )
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
async def other_user(session: AsyncSession) -> User:
    """Create another test user for acceptance tests."""
    user = User(
        id="invitee@example.com",
        email="invitee@example.com",
        name="Test Invitee",
        email_verified=True,
        created_at=datetime.now(UTC),
    )
    session.add(user)
    await session.commit()
    return user
