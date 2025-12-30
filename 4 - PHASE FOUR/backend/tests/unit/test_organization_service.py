"""
Organization Service Unit Tests

Tests for OrganizationService business logic and CRUD operations.

References:
- Task: T027 [P] [US1]
- Spec: specs/005-multi-tenant-collab/spec.md §2.1.1 (Organization Management)
- Constitution v5.0.0 Principle XIX: Multi-Tenancy & Data Isolation Hierarchy
- ADR-001: Multi-Tenant Data Isolation Strategy
"""

import pytest
from datetime import datetime, UTC
from uuid import uuid4, UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Organization, OrganizationMember, User
from app.services.organization_service import OrganizationService
from app.models.exceptions import (
    OrganizationNotFoundError,
    DuplicateSlugError,
    PermissionDeniedError,
)


@pytest.mark.asyncio
class TestOrganizationService:
    """
    Unit tests for OrganizationService.

    Covers:
    - Create organization
    - Read organization (by ID, by slug)
    - Update organization
    - Delete organization (soft delete)
    - List organizations for user
    - Slug uniqueness validation
    """

    async def test_create_organization_success(
        self, session: AsyncSession, test_user: User
    ):
        """
        Test successful organization creation.

        Expected:
        - Organization created with valid UUID
        - Creator is added as OWNER
        - Slug is unique
        - created_at is set to current UTC time
        """
        # Arrange
        org_service = OrganizationService(session)

        # Act
        org = await org_service.create_organization(
            name="Acme Corporation",
            slug="acme-corp",
            description="Innovating the future",
            created_by_user_id=test_user.id
        )

        # Assert organization properties
        assert org.id is not None
        assert isinstance(org.id, UUID)
        assert org.name == "Acme Corporation"
        assert org.slug == "acme-corp"
        assert org.description == "Innovating the future"
        assert org.created_at is not None
        assert org.deleted_at is None

        # Assert creator is owner
        members = await org_service.list_members(
            organization_id=org.id,
            requesting_user_id=test_user.id
        )

        assert len(members) == 1
        assert members[0].user_id == test_user.id
        assert members[0].role == "owner"

    async def test_create_organization_duplicate_slug(
        self, session: AsyncSession, test_user: User
    ):
        """
        Test that duplicate slugs are rejected.

        Expected: DuplicateSlugError raised when slug already exists
        """
        # Arrange
        org_service = OrganizationService(session)

        await org_service.create_organization(
            name="First Org",
            slug="duplicate-slug",
            created_by_user_id=test_user.id
        )

        # Act & Assert
        with pytest.raises(DuplicateSlugError) as exc_info:
            await org_service.create_organization(
                name="Second Org",
                slug="duplicate-slug",  # Same slug
                created_by_user_id=test_user.id
            )

        assert "duplicate-slug" in str(exc_info.value).lower()

    async def test_get_organization_by_id(
        self, session: AsyncSession, test_user: User
    ):
        """
        Test retrieving organization by ID.

        Expected: Organization retrieved successfully with correct attributes
        """
        # Arrange
        org_service = OrganizationService(session)

        created_org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        # Act
        retrieved_org = await org_service.get_organization(
            organization_id=created_org.id,
            user_id=test_user.id
        )

        # Assert
        assert retrieved_org.id == created_org.id
        assert retrieved_org.name == "Test Org"
        assert retrieved_org.slug == "test-org"

    async def test_get_organization_not_found(
        self, session: AsyncSession, test_user: User
    ):
        """
        Test retrieving non-existent organization.

        Expected: OrganizationNotFoundError raised
        """
        # Arrange
        org_service = OrganizationService(session)
        fake_org_id = uuid4()

        # Act & Assert
        with pytest.raises(OrganizationNotFoundError) as exc_info:
            await org_service.get_organization(
                organization_id=fake_org_id,
                user_id=test_user.id
            )

        assert str(fake_org_id) in str(exc_info.value)

    async def test_get_organization_by_slug(
        self, session: AsyncSession, test_user: User
    ):
        """
        Test retrieving organization by slug.

        Expected: Organization retrieved successfully using slug
        """
        # Arrange
        org_service = OrganizationService(session)

        created_org = await org_service.create_organization(
            name="Slug Test Org",
            slug="slug-test",
            created_by_user_id=test_user.id
        )

        # Act
        retrieved_org = await org_service.get_organization_by_slug(
            slug="slug-test",
            user_id=test_user.id
        )

        # Assert
        assert retrieved_org.id == created_org.id
        assert retrieved_org.slug == "slug-test"

    async def test_update_organization_success(
        self, session: AsyncSession, test_user: User
    ):
        """
        Test updating organization details.

        Expected:
        - Name, description can be updated
        - Slug can be updated if unique
        - Only owners/admins can update
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Original Name",
            slug="original-slug",
            description="Original description",
            created_by_user_id=test_user.id
        )

        # Act
        updated_org = await org_service.update_organization(
            organization_id=org.id,
            user_id=test_user.id,
            name="Updated Name",
            description="Updated description"
        )

        # Assert
        assert updated_org.name == "Updated Name"
        assert updated_org.description == "Updated description"
        assert updated_org.slug == "original-slug"  # Slug unchanged

    async def test_update_organization_permission_denied(
        self, session: AsyncSession, test_user: User, other_user: User
    ):
        """
        Test that non-members cannot update organization.

        Expected: PermissionDeniedError raised
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Org",
            slug="test-org",
            created_by_user_id=test_user.id
        )

        # Act & Assert: Other user (non-member) attempts update
        with pytest.raises(PermissionDeniedError):
            await org_service.update_organization(
                organization_id=org.id,
                user_id=other_user.id,  # Not a member
                name="Hacked Name"
            )

    async def test_soft_delete_organization(
        self, session: AsyncSession, test_user: User
    ):
        """
        Test soft deleting organization.

        Expected:
        - deleted_at timestamp is set
        - Organization is hidden from default queries
        - Can be recovered within 30 days
        """
        # Arrange
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="To Be Deleted",
            slug="to-be-deleted",
            created_by_user_id=test_user.id
        )

        # Act
        await org_service.soft_delete_organization(
            organization_id=org.id,
            deleted_by_user_id=test_user.id
        )

        # Assert: deleted_at is set
        deleted_org = await org_service.get_organization(
            organization_id=org.id,
            user_id=test_user.id,
            include_deleted=True
        )

        assert deleted_org.deleted_at is not None
        assert isinstance(deleted_org.deleted_at, datetime)

        # Assert: Not visible in default queries
        with pytest.raises(OrganizationNotFoundError):
            await org_service.get_organization(
                organization_id=org.id,
                user_id=test_user.id,
                include_deleted=False  # Default behavior
            )

    async def test_list_organizations_for_user(
        self, session: AsyncSession, test_user: User, other_user: User
    ):
        """
        Test listing organizations for a user.

        Expected:
        - User sees only organizations they are a member of
        - Ordered by created_at DESC
        - Soft-deleted organizations excluded by default
        """
        # Arrange
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

        org3 = await org_service.create_organization(
            name="Other User Org",
            slug="other-org",
            created_by_user_id=other_user.id
        )

        # Act
        user_orgs = await org_service.list_organizations(
            user_id=test_user.id
        )

        # Assert: User sees only their organizations
        assert len(user_orgs) == 2
        org_ids = {org.id for org in user_orgs}
        assert org1.id in org_ids
        assert org2.id in org_ids
        assert org3.id not in org_ids

        # Assert: Ordered by created_at DESC (org2 should be first)
        assert user_orgs[0].id == org2.id

    async def test_list_organizations_include_deleted(
        self, session: AsyncSession, test_user: User
    ):
        """
        Test listing organizations including soft-deleted ones.

        Expected: Soft-deleted organizations included when include_deleted=True
        """
        # Arrange
        org_service = OrganizationService(session)

        org1 = await org_service.create_organization(
            name="Active Org",
            slug="active-org",
            created_by_user_id=test_user.id
        )

        org2 = await org_service.create_organization(
            name="Deleted Org",
            slug="deleted-org",
            created_by_user_id=test_user.id
        )

        await org_service.soft_delete_organization(
            organization_id=org2.id,
            deleted_by_user_id=test_user.id
        )

        # Act: Query without deleted
        active_orgs = await org_service.list_organizations(
            user_id=test_user.id,
            include_deleted=False
        )

        # Assert: Only active organization visible
        assert len(active_orgs) == 1
        assert active_orgs[0].id == org1.id

        # Act: Query with deleted
        all_orgs = await org_service.list_organizations(
            user_id=test_user.id,
            include_deleted=True
        )

        # Assert: Both organizations visible
        assert len(all_orgs) == 2
        org_ids = {org.id for org in all_orgs}
        assert org1.id in org_ids
        assert org2.id in org_ids


@pytest.fixture
async def test_user(session: AsyncSession) -> User:
    """Create a test user for organization tests."""
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
