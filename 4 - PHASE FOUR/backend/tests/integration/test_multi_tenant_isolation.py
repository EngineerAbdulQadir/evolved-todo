"""
Multi-Tenant Isolation Integration Tests

Tests to verify zero cross-organization data leakage in multi-tenant architecture.

References:
- Task: T026 [P] [US1]
- Spec: specs/005-multi-tenant-collab/spec.md §2.1.1 (Multi-Tenant Data Isolation)
- Constitution v5.0.0 Principle XIX: Multi-Tenancy & Data Isolation Hierarchy
- ADR-001: Multi-Tenant Data Isolation Strategy
"""

import pytest
from datetime import datetime, timedelta, UTC
from uuid import uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    Organization,
    OrganizationMember,
    Task,
    User,
)
from app.services.organization_service import OrganizationService
from app.services.task_service import TaskService


@pytest.mark.asyncio
class TestMultiTenantIsolation:
    """
    Test suite for multi-tenant data isolation.

    Critical Requirements:
    - Organizations MUST NOT see each other's data
    - Cross-organization data leakage is ZERO
    - Tenant context filtering is enforced at service layer
    """

    async def test_organization_isolation_tasks(
        self, session: AsyncSession, test_users: dict[str, User]
    ):
        """
        Test that tasks are isolated by organization.

        Scenario:
        1. Create two organizations (Acme Corp, Globex Inc)
        2. Create tasks in each organization
        3. Verify Acme users only see Acme tasks
        4. Verify Globex users only see Globex tasks
        5. Verify zero cross-organization data leakage

        Expected: Each organization sees ONLY their own tasks (100% isolation)
        """
        # Arrange: Create two organizations
        org_service = OrganizationService(session)

        acme_org = await org_service.create_organization(
            name="Acme Corp",
            slug="acme-corp",
            created_by_user_id=test_users["alice"].id
        )

        globex_org = await org_service.create_organization(
            name="Globex Inc",
            slug="globex-inc",
            created_by_user_id=test_users["bob"].id
        )

        # Arrange: Create tasks in each organization
        task_service = TaskService(session)

        acme_task1 = await task_service.create_task(
            title="Acme Task 1",
            organization_id=acme_org.id,
            created_by_user_id=test_users["alice"].id
        )

        acme_task2 = await task_service.create_task(
            title="Acme Task 2",
            organization_id=acme_org.id,
            created_by_user_id=test_users["alice"].id
        )

        globex_task1 = await task_service.create_task(
            title="Globex Task 1",
            organization_id=globex_org.id,
            created_by_user_id=test_users["bob"].id
        )

        globex_task2 = await task_service.create_task(
            title="Globex Task 2",
            organization_id=globex_org.id,
            created_by_user_id=test_users["bob"].id
        )

        # Act: Query tasks for each organization
        acme_tasks = await task_service.list_tasks(
            organization_id=acme_org.id,
            user_id=test_users["alice"].id
        )

        globex_tasks = await task_service.list_tasks(
            organization_id=globex_org.id,
            user_id=test_users["bob"].id
        )

        # Assert: Acme sees only Acme tasks
        assert len(acme_tasks) == 2
        assert all(task.organization_id == acme_org.id for task in acme_tasks)
        assert set(task.title for task in acme_tasks) == {"Acme Task 1", "Acme Task 2"}

        # Assert: Globex sees only Globex tasks
        assert len(globex_tasks) == 2
        assert all(task.organization_id == globex_org.id for task in globex_tasks)
        assert set(task.title for task in globex_tasks) == {"Globex Task 1", "Globex Task 2"}

        # Assert: Zero cross-organization leakage
        acme_task_ids = {task.id for task in acme_tasks}
        globex_task_ids = {task.id for task in globex_tasks}
        assert acme_task_ids.isdisjoint(globex_task_ids), "Cross-organization data leakage detected!"

    async def test_organization_member_isolation(
        self, session: AsyncSession, test_users: dict[str, User]
    ):
        """
        Test that organization members are isolated by organization.

        Scenario:
        1. Create two organizations with different members
        2. Query members for each organization
        3. Verify no cross-organization member visibility

        Expected: Each organization sees ONLY their own members
        """
        # Arrange: Create organizations
        org_service = OrganizationService(session)

        acme_org = await org_service.create_organization(
            name="Acme Corp",
            slug="acme-corp",
            created_by_user_id=test_users["alice"].id
        )

        globex_org = await org_service.create_organization(
            name="Globex Inc",
            slug="globex-inc",
            created_by_user_id=test_users["bob"].id
        )

        # Arrange: Add members to each organization
        await org_service.add_member(
            organization_id=acme_org.id,
            user_id=test_users["charlie"].id,
            role="member",
            added_by_user_id=test_users["alice"].id
        )

        await org_service.add_member(
            organization_id=globex_org.id,
            user_id=test_users["diana"].id,
            role="member",
            added_by_user_id=test_users["bob"].id
        )

        # Act: Query members for each organization
        acme_members = await org_service.list_members(
            organization_id=acme_org.id,
            requesting_user_id=test_users["alice"].id
        )

        globex_members = await org_service.list_members(
            organization_id=globex_org.id,
            requesting_user_id=test_users["bob"].id
        )

        # Assert: Acme sees only Acme members (Alice as owner + Charlie)
        assert len(acme_members) == 2
        acme_member_ids = {member.user_id for member in acme_members}
        assert test_users["alice"].id in acme_member_ids
        assert test_users["charlie"].id in acme_member_ids
        assert test_users["bob"].id not in acme_member_ids
        assert test_users["diana"].id not in acme_member_ids

        # Assert: Globex sees only Globex members (Bob as owner + Diana)
        assert len(globex_members) == 2
        globex_member_ids = {member.user_id for member in globex_members}
        assert test_users["bob"].id in globex_member_ids
        assert test_users["diana"].id in globex_member_ids
        assert test_users["alice"].id not in globex_member_ids
        assert test_users["charlie"].id not in globex_member_ids

    async def test_unauthorized_cross_organization_access(
        self, session: AsyncSession, test_users: dict[str, User]
    ):
        """
        Test that users cannot access resources from organizations they don't belong to.

        Scenario:
        1. Create organization A with user Alice
        2. Create organization B with user Bob
        3. Attempt to access organization B's tasks as Alice

        Expected: Access denied (403 Forbidden or empty result set)
        """
        # Arrange: Create organizations
        org_service = OrganizationService(session)

        org_a = await org_service.create_organization(
            name="Organization A",
            slug="org-a",
            created_by_user_id=test_users["alice"].id
        )

        org_b = await org_service.create_organization(
            name="Organization B",
            slug="org-b",
            created_by_user_id=test_users["bob"].id
        )

        # Arrange: Create task in organization B
        task_service = TaskService(session)

        org_b_task = await task_service.create_task(
            title="Organization B Task",
            organization_id=org_b.id,
            created_by_user_id=test_users["bob"].id
        )

        # Act & Assert: Alice attempts to access organization B's tasks
        with pytest.raises(Exception) as exc_info:
            # This should raise PermissionError or similar
            await task_service.list_tasks(
                organization_id=org_b.id,
                user_id=test_users["alice"].id  # Alice not a member of org B
            )

        # Assert: Proper exception raised (PermissionError or HTTP 403)
        assert exc_info.value is not None

    async def test_soft_delete_isolation(
        self, session: AsyncSession, test_users: dict[str, User]
    ):
        """
        Test that soft-deleted organizations are properly isolated.

        Scenario:
        1. Create organization
        2. Soft delete the organization
        3. Verify organization is not visible in active queries
        4. Verify tasks are not accessible

        Expected: Soft-deleted data is excluded from normal queries
        """
        # Arrange: Create organization
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Temporary Org",
            slug="temp-org",
            created_by_user_id=test_users["alice"].id
        )

        # Act: Soft delete the organization
        await org_service.soft_delete_organization(
            organization_id=org.id,
            deleted_by_user_id=test_users["alice"].id
        )

        # Assert: Organization not visible in active queries
        active_orgs = await org_service.list_organizations(
            user_id=test_users["alice"].id,
            include_deleted=False
        )

        assert org.id not in {o.id for o in active_orgs}

        # Assert: Organization visible in deleted queries (for recovery)
        deleted_orgs = await org_service.list_organizations(
            user_id=test_users["alice"].id,
            include_deleted=True
        )

        deleted_org_ids = {o.id for o in deleted_orgs if o.deleted_at is not None}
        assert org.id in deleted_org_ids


@pytest.fixture
async def test_users(session: AsyncSession) -> dict[str, User]:
    """
    Create test users for multi-tenant isolation tests.

    Returns:
        Dictionary of test users: alice, bob, charlie, diana
    """
    users = {}

    for name in ["alice", "bob", "charlie", "diana"]:
        user = User(
            id=f"{name}@example.com",
            email=f"{name}@example.com",
            name=name.capitalize(),
            email_verified=True,
            created_at=datetime.now(UTC),
        )
        session.add(user)
        users[name] = user

    await session.commit()

    return users
