"""
Organization API Integration Tests

End-to-end tests for organization management API endpoints.

References:
- Task: T029 [P] [US1]
- Spec: specs/005-multi-tenant-collab/spec.md §2.1.1 (Organization Management)
- Constitution v5.0.0 Principle XIX: Multi-Tenancy & Data Isolation Hierarchy
- ADR-001: Multi-Tenant Data Isolation Strategy
- ADR-002: RBAC Middleware Architecture
"""

import pytest
from datetime import datetime, UTC
from uuid import uuid4

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User, Organization
from app.services.organization_service import OrganizationService


@pytest.mark.asyncio
class TestOrganizationAPI:
    """
    Integration tests for Organization API endpoints.

    Endpoints tested:
    - POST /api/organizations - Create organization
    - GET /api/organizations - List user's organizations
    - GET /api/organizations/{org_id} - Get organization details
    - GET /api/organizations/slug/{slug} - Get organization by slug
    - PATCH /api/organizations/{org_id} - Update organization
    - DELETE /api/organizations/{org_id} - Soft delete organization
    - GET /api/organizations/{org_id}/members - List organization members
    - POST /api/organizations/{org_id}/members - Add member
    - DELETE /api/organizations/{org_id}/members/{user_id} - Remove member
    """

    async def test_create_organization_success(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """
        Test POST /api/organizations - successful creation.

        Expected: 201 Created with organization details
        """
        # Arrange
        payload = {
            "name": "Acme Corporation",
            "slug": "acme-corp",
            "description": "We make everything"
        }

        # Act
        response = await client.post(
            "/api/organizations",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "Acme Corporation"
        assert data["slug"] == "acme-corp"
        assert data["description"] == "We make everything"
        assert "id" in data
        assert "created_at" in data
        assert data["deleted_at"] is None

    async def test_create_organization_duplicate_slug(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        """
        Test POST /api/organizations - duplicate slug rejection.

        Expected: 400 Bad Request with error message
        """
        # Arrange: Create first organization
        payload = {
            "name": "First Org",
            "slug": "duplicate-slug",
        }

        await client.post(
            "/api/organizations",
            json=payload,
            headers=auth_headers
        )

        # Act: Attempt to create second organization with same slug
        payload2 = {
            "name": "Second Org",
            "slug": "duplicate-slug",  # Same slug
        }

        response = await client.post(
            "/api/organizations",
            json=payload2,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 400
        assert "slug" in response.json()["detail"].lower()

    async def test_create_organization_unauthenticated(
        self, client: AsyncClient
    ):
        """
        Test POST /api/organizations - unauthenticated request.

        Expected: 401 Unauthorized
        """
        # Arrange
        payload = {
            "name": "Unauthorized Org",
            "slug": "unauthorized",
        }

        # Act
        response = await client.post(
            "/api/organizations",
            json=payload
            # No auth headers
        )

        # Assert
        assert response.status_code == 401

    async def test_list_organizations(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test GET /api/organizations - list user's organizations.

        Expected: 200 OK with list of organizations user is a member of
        """
        # Arrange: Create multiple organizations
        org_service = OrganizationService(session)

        org1 = await org_service.create_organization(
            name="Org 1",
            slug="org-1",
            created_by_user_id=test_user.id
        )

        org2 = await org_service.create_organization(
            name="Org 2",
            slug="org-2",
            created_by_user_id=test_user.id
        )

        # Act
        response = await client.get(
            "/api/organizations",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        org_slugs = {org["slug"] for org in data}
        assert "org-1" in org_slugs
        assert "org-2" in org_slugs

    async def test_get_organization_by_id(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test GET /api/organizations/{org_id} - get organization details.

        Expected: 200 OK with organization details
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            description="Test description",
            created_by_user_id=test_user.id
        )

        # Act
        response = await client.get(
            f"/api/organizations/{org.id}",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(org.id)
        assert data["name"] == "Test Org"
        assert data["slug"] == "test-org"
        assert data["description"] == "Test description"

    async def test_get_organization_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Test GET /api/organizations/{org_id} - non-existent organization.

        Expected: 404 Not Found
        """
        # Arrange
        fake_org_id = uuid4()

        # Act
        response = await client.get(
            f"/api/organizations/{fake_org_id}",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 404

    async def test_get_organization_by_slug(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test GET /api/organizations/slug/{slug} - get by slug.

        Expected: 200 OK with organization details
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Slug Test",
            slug="slug-test-org",
            created_by_user_id=test_user.id
        )

        # Act
        response = await client.get(
            "/api/organizations/slug/slug-test-org",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["slug"] == "slug-test-org"
        assert data["id"] == str(org.id)

    async def test_update_organization_success(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test PATCH /api/organizations/{org_id} - update organization.

        Expected: 200 OK with updated organization
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Original Name",
            slug="original-slug",
            description="Original description",
            created_by_user_id=test_user.id
        )

        update_payload = {
            "name": "Updated Name",
            "description": "Updated description"
        }

        # Act
        response = await client.patch(
            f"/api/organizations/{org.id}",
            json=update_payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert data["slug"] == "original-slug"  # Slug unchanged

    async def test_update_organization_permission_denied(
        self, client: AsyncClient, other_auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test PATCH /api/organizations/{org_id} - permission denied.

        Expected: 403 Forbidden
        """
        # Arrange: Create organization as test_user
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        update_payload = {
            "name": "Hacked Name"
        }

        # Act: Other user attempts to update
        response = await client.patch(
            f"/api/organizations/{org.id}",
            json=update_payload,
            headers=other_auth_headers  # Different user
        )

        # Assert
        assert response.status_code == 403

    async def test_delete_organization_soft_delete(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User
    ):
        """
        Test DELETE /api/organizations/{org_id} - soft delete.

        Expected: 204 No Content, organization soft deleted
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="To Be Deleted",
            slug="to-be-deleted",
            created_by_user_id=test_user.id
        )

        # Act
        response = await client.delete(
            f"/api/organizations/{org.id}",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 204

        # Verify organization is soft deleted
        deleted_org = await org_service.get_organization(
            organization_id=org.id,
            user_id=test_user.id,
            include_deleted=True
        )

        assert deleted_org.deleted_at is not None

    async def test_list_organization_members(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User, other_user: User
    ):
        """
        Test GET /api/organizations/{org_id}/members - list members.

        Expected: 200 OK with list of organization members
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        # Add another member
        await org_service.add_member(
            organization_id=org.id,
            user_id=other_user.id,
            role="member",
            added_by_user_id=test_user.id
        )

        # Act
        response = await client.get(
            f"/api/organizations/{org.id}/members",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        user_ids = {member["user_id"] for member in data}
        assert test_user.id in user_ids
        assert other_user.id in user_ids

    async def test_add_organization_member(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User, other_user: User
    ):
        """
        Test POST /api/organizations/{org_id}/members - add member.

        Expected: 201 Created with member details
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        payload = {
            "user_id": other_user.id,
            "role": "admin"
        }

        # Act
        response = await client.post(
            f"/api/organizations/{org.id}/members",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 201
        data = response.json()

        assert data["user_id"] == other_user.id
        assert data["role"] == "admin"

    async def test_remove_organization_member(
        self, client: AsyncClient, auth_headers: dict, session: AsyncSession, test_user: User, other_user: User
    ):
        """
        Test DELETE /api/organizations/{org_id}/members/{user_id} - remove member.

        Expected: 204 No Content
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        # Add member
        await org_service.add_member(
            organization_id=org.id,
            user_id=other_user.id,
            role="member",
            added_by_user_id=test_user.id
        )

        # Act
        response = await client.delete(
            f"/api/organizations/{org.id}/members/{other_user.id}",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 204

        # Verify member removed
        members = await org_service.list_members(
            organization_id=org.id,
            requesting_user_id=test_user.id
        )

        member_ids = {member.user_id for member in members}
        assert other_user.id not in member_ids


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
    """Create another test user for permission tests."""
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
