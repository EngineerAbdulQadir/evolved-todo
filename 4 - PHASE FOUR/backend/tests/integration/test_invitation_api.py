"""
Invitation API Integration Tests

End-to-end tests for invitation system API endpoints.

References:
- Task: T030 [P] [US1]
- Spec: specs/005-multi-tenant-collab/spec.md §2.1.2 (Invitation System)
- Constitution v5.0.0 Principle XXIII: Invitation System & User Onboarding
- ADR-004: Invitation System Security Design
"""

import pytest
from datetime import datetime, timedelta, UTC
from uuid import uuid4

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, Organization
from app.services.organization_service import OrganizationService
from app.services.invitation_service import InvitationService


@pytest.mark.asyncio
class TestInvitationAPI:
    """
    Integration tests for Invitation API endpoints.

    Endpoints tested:
    - POST /api/invitations - Create invitation
    - GET /api/invitations/token/{token} - Get invitation by token
    - POST /api/invitations/{token}/accept - Accept invitation
    - DELETE /api/invitations/{invitation_id} - Revoke invitation
    - GET /api/organizations/{org_id}/invitations - List pending invitations
    """

    async def test_create_invitation_success(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test POST /api/invitations - successful creation.

        Expected: 201 Created with invitation details and secure token
        """
        # Arrange: Create organization
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        payload = {
            "organization_id": str(org.id),
            "email": "newuser@example.com",
            "role": "member"
        }

        # Act
        response = await client.post(
            "/api/invitations",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 201
        data = response.json()

        assert data["email"] == "newuser@example.com"
        assert data["role"] == "member"
        assert data["organization_id"] == str(org.id)
        assert "token" in data
        assert len(data["token"]) >= 40  # 256-bit token
        assert "expires_at" in data
        assert data["accepted_at"] is None

    async def test_create_invitation_with_team(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test POST /api/invitations - invitation with team assignment.

        Expected: 201 Created with team_id included
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        team_id = uuid4()

        payload = {
            "organization_id": str(org.id),
            "team_id": str(team_id),
            "email": "teamuser@example.com",
            "role": "member"
        }

        # Act
        response = await client.post(
            "/api/invitations",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 201
        data = response.json()

        assert data["team_id"] == str(team_id)

    async def test_create_invitation_permission_denied(
        self, client: AsyncClient, other_auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test POST /api/invitations - permission denied for non-members.

        Expected: 403 Forbidden
        """
        # Arrange: Create organization as test_user
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        payload = {
            "organization_id": str(org.id),
            "email": "hacker@example.com",
            "role": "owner"
        }

        # Act: Other user attempts to create invitation
        response = await client.post(
            "/api/invitations",
            json=payload,
            headers=other_auth_headers  # Different user
        )

        # Assert
        assert response.status_code == 403

    async def test_create_invitation_unauthenticated(
        self, client: AsyncClient, session: AsyncSession, test_user: User
    ):
        """
        Test POST /api/invitations - unauthenticated request.

        Expected: 401 Unauthorized
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        payload = {
            "organization_id": str(org.id),
            "email": "unauthorized@example.com",
            "role": "member"
        }

        # Act
        response = await client.post(
            "/api/invitations",
            json=payload
            # No auth headers
        )

        # Assert
        assert response.status_code == 401

    async def test_get_invitation_by_token(
        self, client: AsyncClient, session: AsyncSession, test_user: User
    ):
        """
        Test GET /api/invitations/token/{token} - get invitation details.

        Expected: 200 OK with invitation details (no auth required for public lookup)
        """
        # Arrange: Create invitation
        org_service = OrganizationService(session)
        invitation_service = InvitationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        invitation = await invitation_service.create_invitation(
            organization_id=org.id,
            email="invitee@example.com",
            role="member",
            invited_by_user_id=test_user.id
        )

        # Act: Public endpoint (no auth required)
        response = await client.get(
            f"/api/invitations/token/{invitation.token}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["email"] == "invitee@example.com"
        assert data["role"] == "member"
        assert data["token"] == invitation.token

    async def test_get_invitation_not_found(
        self, client: AsyncClient
    ):
        """
        Test GET /api/invitations/token/{token} - non-existent token.

        Expected: 404 Not Found
        """
        # Arrange
        fake_token = "fake_token_12345"

        # Act
        response = await client.get(
            f"/api/invitations/token/{fake_token}"
        )

        # Assert
        assert response.status_code == 404

    async def test_accept_invitation_success(
        self, client: AsyncClient, other_auth_headers: dict, session: AsyncSession, test_user: User, other_user: User
    ):
        """
        Test POST /api/invitations/{token}/accept - successful acceptance.

        Expected:
        - 200 OK
        - User added to organization
        - Invitation marked as accepted
        """
        # Arrange: Create invitation
        org_service = OrganizationService(session)
        invitation_service = InvitationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        invitation = await invitation_service.create_invitation(
            organization_id=org.id,
            email=other_user.email,
            role="member",
            invited_by_user_id=test_user.id
        )

        # Act: Other user accepts invitation
        response = await client.post(
            f"/api/invitations/{invitation.token}/accept",
            headers=other_auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Invitation accepted successfully"
        assert "organization_id" in data

        # Verify user is now a member
        members = await org_service.list_members(
            organization_id=org.id,
            requesting_user_id=test_user.id
        )

        member_ids = {member.user_id for member in members}
        assert other_user.id in member_ids

    async def test_accept_invitation_expired(
        self, client: AsyncClient, other_auth_headers: dict, session: AsyncSession, test_user: User, other_user: User
    ):
        """
        Test POST /api/invitations/{token}/accept - expired invitation.

        Expected: 400 Bad Request with expiration error
        """
        # Arrange: Create invitation
        org_service = OrganizationService(session)
        invitation_service = InvitationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        invitation = await invitation_service.create_invitation(
            organization_id=org.id,
            email=other_user.email,
            role="member",
            invited_by_user_id=test_user.id
        )

        # Manually expire the invitation
        invitation.expires_at = datetime.now(UTC) - timedelta(days=1)
        session.add(invitation)
        await session.commit()

        # Act: Attempt to accept expired invitation
        response = await client.post(
            f"/api/invitations/{invitation.token}/accept",
            headers=other_auth_headers
        )

        # Assert
        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()

    async def test_accept_invitation_already_accepted(
        self, client: AsyncClient, other_auth_headers: dict, session: AsyncSession, test_user: User, other_user: User
    ):
        """
        Test POST /api/invitations/{token}/accept - already accepted.

        Expected: 400 Bad Request with already accepted error
        """
        # Arrange: Create and accept invitation
        org_service = OrganizationService(session)
        invitation_service = InvitationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        invitation = await invitation_service.create_invitation(
            organization_id=org.id,
            email=other_user.email,
            role="member",
            invited_by_user_id=test_user.id
        )

        # First acceptance
        await invitation_service.accept_invitation(
            token=invitation.token,
            accepting_user_id=other_user.id
        )

        # Act: Attempt second acceptance
        response = await client.post(
            f"/api/invitations/{invitation.token}/accept",
            headers=other_auth_headers
        )

        # Assert
        assert response.status_code == 400
        assert "already accepted" in response.json()["detail"].lower()

    async def test_revoke_invitation(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test DELETE /api/invitations/{invitation_id} - revoke invitation.

        Expected: 204 No Content
        """
        # Arrange: Create invitation
        org_service = OrganizationService(session)
        invitation_service = InvitationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        invitation = await invitation_service.create_invitation(
            organization_id=org.id,
            email="revoked@example.com",
            role="member",
            invited_by_user_id=test_user.id
        )

        # Act
        response = await client.delete(
            f"/api/invitations/{invitation.id}",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 204

        # Verify invitation is revoked (not retrievable)
        lookup_response = await client.get(
            f"/api/invitations/token/{invitation.token}"
        )

        assert lookup_response.status_code == 404

    async def test_list_pending_invitations(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User, other_user: User
    ):
        """
        Test GET /api/organizations/{org_id}/invitations - list pending.

        Expected: 200 OK with list of pending invitations (accepted excluded)
        """
        # Arrange: Create organization and invitations
        org_service = OrganizationService(session)
        invitation_service = InvitationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        # Create pending invitation
        pending_inv = await invitation_service.create_invitation(
            organization_id=org.id,
            email="pending@example.com",
            role="member",
            invited_by_user_id=test_user.id
        )

        # Create and accept invitation
        accepted_inv = await invitation_service.create_invitation(
            organization_id=org.id,
            email=other_user.email,
            role="member",
            invited_by_user_id=test_user.id
        )

        await invitation_service.accept_invitation(
            token=accepted_inv.token,
            accepting_user_id=other_user.id
        )

        # Act
        response = await client.get(
            f"/api/organizations/{org.id}/invitations",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Only pending invitation should be returned
        assert len(data) == 1
        assert data[0]["id"] == str(pending_inv.id)
        assert data[0]["email"] == "pending@example.com"
        assert data[0]["accepted_at"] is None

    async def test_list_invitations_permission_denied(
        self, client: AsyncClient, other_auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test GET /api/organizations/{org_id}/invitations - permission denied.

        Expected: 403 Forbidden for non-members
        """
        # Arrange: Create organization as test_user
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        # Act: Other user attempts to list invitations
        response = await client.get(
            f"/api/organizations/{org.id}/invitations",
            headers=other_auth_headers  # Different user
        )

        # Assert
        assert response.status_code == 403

    async def test_invitation_email_validation(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test POST /api/invitations - invalid email validation.

        Expected: 400 Bad Request for invalid email format
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        payload = {
            "organization_id": str(org.id),
            "email": "invalid-email-format",  # Invalid email
            "role": "member"
        }

        # Act
        response = await client.post(
            "/api/invitations",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()


@pytest.fixture
async def test_user(session: AsyncSession) -> User:
    """Create a test user for API tests."""
    user = User(
        id="test@example.com",
        email="test@example.com",
        name="Test User",
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
        id="other@example.com",
        email="other@example.com",
        name="Other User",
        email_verified=True,
        created_at=datetime.now(UTC),
    )
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    """Generate JWT authentication headers for test_user."""
    # TODO: Implement JWT token generation
    # For now, return mock headers
    token = "mock_jwt_token_for_test_user"
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def other_auth_headers(other_user: User) -> dict:
    """Generate JWT authentication headers for other_user."""
    # TODO: Implement JWT token generation
    # For now, return mock headers
    token = "mock_jwt_token_for_other_user"
    return {"Authorization": f"Bearer {token}"}
