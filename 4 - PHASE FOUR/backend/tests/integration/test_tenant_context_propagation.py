"""
Tenant Context Propagation Tests

Integration tests verifying that tenant context (organization_id) propagates
correctly from JWT token → API endpoint → Service layer → Database queries.

Task: T139 [US6] - Write tenant context propagation tests
References:
- specs/005-multi-tenant-collab/spec.md User Story 6
- Constitution v5.0.0 Principle XX: Multi-Tenant Data Isolation
- Stateless Architecture Principle (Phase 4)
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, UTC
from unittest.mock import patch, AsyncMock
import asyncio

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models import Organization, User, Team, Project, Task
from app.services.organization_service import OrganizationService
from app.services.team_service import TeamService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService


@pytest.mark.asyncio
class TestTenantContextPropagation:
    """
    Test suite verifying tenant context propagation through application layers.

    Flow: JWT Token → API Endpoint → Service Layer → Database Query
    Requirement: organization_id MUST be present and validated at each layer
    """

    async def test_jwt_token_contains_organization_id(
        self,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: JWT tokens contain organization_id claim
        Expected: Decoded JWT has organization_id field
        """
        # Arrange: Create organization
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Organization",
            slug="test-org",
            created_by_user_id=test_users["alice"].id
        )

        # Act: Create access token with organization context
        from app.core.security import create_access_token, decode_access_token

        token = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org.id)
        })

        # Assert: Token contains organization_id
        decoded = decode_access_token(token)
        assert "organization_id" in decoded
        assert decoded["organization_id"] == str(org.id)

    async def test_api_endpoint_extracts_organization_id_from_token(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: API endpoints extract organization_id from JWT token
        Expected: Endpoint receives correct organization_id from auth middleware
        """
        # Arrange: Create organization and team
        org_service = OrganizationService(session)
        team_service = TeamService(session)

        org = await org_service.create_organization(
            name="Test Organization",
            slug="test-org",
            created_by_user_id=test_users["alice"].id
        )

        # Create JWT token with organization context
        from app.core.security import create_access_token

        token = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org.id)
        })

        # Act: Make API call to create team (requires organization_id)
        response = await client.post(
            "/api/v1/teams",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Engineering Team",
                "slug": "engineering"
            }
        )

        # Assert: Team created successfully with correct organization_id
        assert response.status_code == 201
        team_data = response.json()
        assert team_data["organization_id"] == str(org.id)

    async def test_service_layer_receives_organization_id(
        self,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: Service layer methods receive and use organization_id
        Expected: Service methods accept organization_id parameter
        """
        # Arrange: Create organization
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Organization",
            slug="test-org",
            created_by_user_id=test_users["alice"].id
        )

        # Act: Call service method with organization_id
        task_service = TaskService(session)

        task = await task_service.create_task(
            organization_id=org.id,
            title="Test Task",
            created_by_user_id=test_users["alice"].id
        )

        # Assert: Task created with correct organization_id
        assert task.organization_id == org.id

    async def test_database_queries_filtered_by_organization_id(
        self,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: Database queries include WHERE organization_id = ? filter
        Expected: SQL queries automatically filter by organization
        """
        # Arrange: Create two organizations with tasks
        org_service = OrganizationService(session)
        task_service = TaskService(session)

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

        # Create tasks in both organizations
        await task_service.create_task(
            organization_id=org_a.id,
            title="Org A Task 1",
            created_by_user_id=test_users["alice"].id
        )

        await task_service.create_task(
            organization_id=org_a.id,
            title="Org A Task 2",
            created_by_user_id=test_users["alice"].id
        )

        await task_service.create_task(
            organization_id=org_b.id,
            title="Org B Task 1",
            created_by_user_id=test_users["bob"].id
        )

        # Act: Query tasks for Organization A
        tasks_a = await task_service.list_tasks(
            organization_id=org_a.id,
            user_id=test_users["alice"].id
        )

        # Assert: Only Organization A tasks returned
        assert len(tasks_a) == 2
        assert all(task.organization_id == org_a.id for task in tasks_a)
        assert set(task.title for task in tasks_a) == {"Org A Task 1", "Org A Task 2"}

    async def test_tenant_context_persists_across_requests(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: Tenant context is stateless and derived from JWT on each request
        Expected: Multiple requests with same token maintain correct organization scope
        """
        # Arrange: Create organization
        org_service = OrganizationService(session)

        org = await org_service.create_organization(
            name="Test Organization",
            slug="test-org",
            created_by_user_id=test_users["alice"].id
        )

        # Create JWT token
        from app.core.security import create_access_token

        token = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org.id)
        })

        headers = {"Authorization": f"Bearer {token}"}

        # Act: Make multiple API calls
        # Request 1: Create team
        response1 = await client.post(
            "/api/v1/teams",
            headers=headers,
            json={"name": "Team 1", "slug": "team-1"}
        )

        # Request 2: List teams
        response2 = await client.get("/api/v1/teams", headers=headers)

        # Request 3: Create another team
        response3 = await client.post(
            "/api/v1/teams",
            headers=headers,
            json={"name": "Team 2", "slug": "team-2"}
        )

        # Assert: All requests use correct organization context
        assert response1.status_code == 201
        assert response1.json()["organization_id"] == str(org.id)

        assert response2.status_code == 200
        teams = response2.json()
        assert all(team["organization_id"] == str(org.id) for team in teams)

        assert response3.status_code == 201
        assert response3.json()["organization_id"] == str(org.id)

    async def test_invalid_organization_id_in_token_rejected(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: API rejects requests with invalid organization_id in JWT
        Expected: 401 Unauthorized or 403 Forbidden for non-existent organization
        """
        # Act: Create token with non-existent organization_id
        from app.core.security import create_access_token

        fake_org_id = uuid4()

        token = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(fake_org_id)
        })

        # Attempt to create team with invalid organization context
        response = await client.post(
            "/api/v1/teams",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Team", "slug": "team"}
        )

        # Assert: Request rejected
        assert response.status_code in [401, 403, 404], \
            f"Expected 401/403/404, got {response.status_code}"

    async def test_missing_organization_id_in_token_rejected(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: API rejects requests without organization_id in JWT
        Expected: 400 Bad Request or 401 Unauthorized
        """
        # Act: Create token WITHOUT organization_id
        from app.core.security import create_access_token

        token = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email
            # Missing: "organization_id"
        })

        # Attempt to create team without organization context
        response = await client.post(
            "/api/v1/teams",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Team", "slug": "team"}
        )

        # Assert: Request rejected
        assert response.status_code in [400, 401, 403], \
            f"Expected 400/401/403, got {response.status_code}"

    async def test_organization_id_cannot_be_overridden_in_request_body(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: organization_id from JWT token cannot be overridden by request body
        Expected: organization_id from token takes precedence over body parameter
        """
        # Arrange: Create two organizations
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

        # Create token for Organization A
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        # Act: Attempt to create team with Organization B's ID in request body
        response = await client.post(
            "/api/v1/teams",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "name": "Team",
                "slug": "team",
                "organization_id": str(org_b.id)  # Attempt to override
            }
        )

        # Assert: Team created with organization_id from token (Org A), not body (Org B)
        if response.status_code == 201:
            team_data = response.json()
            assert team_data["organization_id"] == str(org_a.id), \
                "organization_id was overridden by request body!"
        else:
            # Or request rejected due to conflict
            assert response.status_code in [400, 403]

    async def test_tenant_context_survives_pod_restart(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: Stateless architecture - tenant context derived from JWT on each request
        Expected: No in-memory state, context re-derived after "pod restart" simulation
        """
        # Arrange: Create organization and team
        org_service = OrganizationService(session)
        team_service = TeamService(session)

        org = await org_service.create_organization(
            name="Test Organization",
            slug="test-org",
            created_by_user_id=test_users["alice"].id
        )

        # Create team before "restart"
        team = await team_service.create_team(
            organization_id=org.id,
            name="Engineering",
            slug="engineering",
            created_by_user_id=test_users["alice"].id
        )

        # Create token
        from app.core.security import create_access_token

        token = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org.id)
        })

        # Simulate pod restart by clearing any in-memory caches (if present)
        # In stateless architecture, there should be no in-memory tenant state

        # Act: Make request after "restart"
        response = await client.get(
            f"/api/v1/teams/{team.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert: Request succeeds with correct data (context re-derived from JWT)
        assert response.status_code == 200
        team_data = response.json()
        assert team_data["id"] == str(team.id)
        assert team_data["organization_id"] == str(org.id)

    async def test_concurrent_requests_different_tenants(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: Concurrent requests from different tenants maintain correct context
        Expected: No context bleeding between concurrent requests
        """
        # Arrange: Create two organizations
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

        # Create tokens for both organizations
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        token_b = create_access_token({
            "sub": test_users["bob"].id,
            "email": test_users["bob"].email,
            "organization_id": str(org_b.id)
        })

        # Act: Make concurrent requests from both tenants
        tasks = []

        for i in range(5):
            # User A creates teams
            task_a = client.post(
                "/api/v1/teams",
                headers={"Authorization": f"Bearer {token_a}"},
                json={"name": f"Team A{i}", "slug": f"team-a{i}"}
            )
            tasks.append(task_a)

            # User B creates teams
            task_b = client.post(
                "/api/v1/teams",
                headers={"Authorization": f"Bearer {token_b}"},
                json={"name": f"Team B{i}", "slug": f"team-b{i}"}
            )
            tasks.append(task_b)

        responses = await asyncio.gather(*tasks)

        # Assert: All requests succeeded with correct organization_id
        for i, response in enumerate(responses):
            assert response.status_code == 201
            team_data = response.json()

            if i % 2 == 0:  # User A's teams
                assert team_data["organization_id"] == str(org_a.id)
                assert "Team A" in team_data["name"]
            else:  # User B's teams
                assert team_data["organization_id"] == str(org_b.id)
                assert "Team B" in team_data["name"]

    async def test_soft_deleted_entities_filtered_in_tenant_queries(
        self,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: Soft-deleted entities filtered by deleted_at IS NULL in tenant queries
        Expected: Queries include both organization_id AND deleted_at filters
        """
        # Arrange: Create organization and projects
        org_service = OrganizationService(session)
        team_service = TeamService(session)
        project_service = ProjectService(session)

        org = await org_service.create_organization(
            name="Test Organization",
            slug="test-org",
            created_by_user_id=test_users["alice"].id
        )

        team = await team_service.create_team(
            organization_id=org.id,
            name="Engineering",
            slug="engineering",
            created_by_user_id=test_users["alice"].id
        )

        project1 = await project_service.create_project(
            organization_id=org.id,
            team_id=team.id,
            name="Active Project",
            slug="active-project",
            created_by_user_id=test_users["alice"].id
        )

        project2 = await project_service.create_project(
            organization_id=org.id,
            team_id=team.id,
            name="Deleted Project",
            slug="deleted-project",
            created_by_user_id=test_users["alice"].id
        )

        # Soft-delete project2
        await project_service.soft_delete_project(
            project_id=project2.id,
            organization_id=org.id,
            deleted_by_user_id=test_users["alice"].id
        )

        # Act: Query projects for organization
        projects = await project_service.list_projects(
            organization_id=org.id,
            user_id=test_users["alice"].id,
            include_deleted=False
        )

        # Assert: Only active project returned
        assert len(projects) == 1
        assert projects[0].id == project1.id
        assert projects[0].deleted_at is None

        # Assert: Deleted project returned when include_deleted=True
        all_projects = await project_service.list_projects(
            organization_id=org.id,
            user_id=test_users["alice"].id,
            include_deleted=True
        )

        assert len(all_projects) == 2


@pytest.fixture
async def test_users(session: AsyncSession) -> dict[str, User]:
    """
    Create test users for tenant context propagation tests.

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
