"""
Cross-Organization Access Denial Tests

Integration tests verifying 404/403 responses when users attempt to access
resources from organizations they don't belong to.

Task: T138 [US6] - Write cross-org access denial tests (404/403 for other org's resources)
References:
- specs/005-multi-tenant-collab/spec.md User Story 6
- Constitution v5.0.0 Principle XX: Multi-Tenant Data Isolation
- ADR-003: Soft Delete and Audit Trail Strategy
"""

import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, UTC

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Organization, User, Team, Project, Task
from app.services.organization_service import OrganizationService
from app.services.team_service import TeamService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService


@pytest.mark.asyncio
class TestCrossOrgAccessDenial:
    """
    Test suite verifying that users cannot access resources from other organizations.

    Expected Behavior:
    - Accessing another org's resources returns 404 (Not Found) or 403 (Forbidden)
    - User's own resources return 200 (OK)
    - No data leakage through error messages
    """

    async def test_access_other_org_details_returns_404_or_403(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: User A cannot view Organization B's details
        Expected: GET /organizations/{org_b_id} returns 404 or 403
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

        # Act: User A attempts to access Organization B's details
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        response = await client.get(
            f"/api/v1/organizations/{org_b.id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Assert: Access denied
        assert response.status_code in [403, 404], \
            f"Expected 403/404, got {response.status_code}"

        # Assert: User A can access their own org
        response_own = await client.get(
            f"/api/v1/organizations/{org_a.id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert response_own.status_code == 200

    async def test_access_other_org_teams_returns_empty_or_403(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: User A cannot view Organization B's teams
        Expected: GET /teams returns empty list (filtered) or 403
        """
        # Arrange: Create organizations and teams
        org_service = OrganizationService(session)
        team_service = TeamService(session)

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

        # Create team in Organization B
        team_b = await team_service.create_team(
            organization_id=org_b.id,
            name="Team B",
            slug="team-b",
            created_by_user_id=test_users["bob"].id
        )

        # Act: User A attempts to access Team B's details
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        response = await client.get(
            f"/api/v1/teams/{team_b.id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Assert: Access denied
        assert response.status_code in [403, 404], \
            f"Expected 403/404, got {response.status_code}"

    async def test_access_other_org_projects_returns_404_or_403(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: User A cannot view Organization B's projects
        Expected: GET /projects/{project_b_id} returns 404 or 403
        """
        # Arrange: Create organizations, teams, and projects
        org_service = OrganizationService(session)
        team_service = TeamService(session)
        project_service = ProjectService(session)

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

        team_b = await team_service.create_team(
            organization_id=org_b.id,
            name="Team B",
            slug="team-b",
            created_by_user_id=test_users["bob"].id
        )

        project_b = await project_service.create_project(
            organization_id=org_b.id,
            team_id=team_b.id,
            name="Project B",
            slug="project-b",
            created_by_user_id=test_users["bob"].id
        )

        # Act: User A attempts to access Project B
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        response = await client.get(
            f"/api/v1/projects/{project_b.id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Assert: Access denied
        assert response.status_code in [403, 404], \
            f"Expected 403/404, got {response.status_code}"

    async def test_access_other_org_tasks_returns_404_or_403(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: User A cannot view Organization B's tasks
        Expected: GET /tasks/{task_b_id} returns 404 or 403
        """
        # Arrange: Create full hierarchy for Organization B
        org_service = OrganizationService(session)
        team_service = TeamService(session)
        project_service = ProjectService(session)
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

        team_b = await team_service.create_team(
            organization_id=org_b.id,
            name="Team B",
            slug="team-b",
            created_by_user_id=test_users["bob"].id
        )

        project_b = await project_service.create_project(
            organization_id=org_b.id,
            team_id=team_b.id,
            name="Project B",
            slug="project-b",
            created_by_user_id=test_users["bob"].id
        )

        task_b = await task_service.create_task(
            organization_id=org_b.id,
            team_id=team_b.id,
            project_id=project_b.id,
            title="Task B",
            created_by_user_id=test_users["bob"].id
        )

        # Act: User A attempts to access Task B
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        response = await client.get(
            f"/api/v1/tasks/{task_b.id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Assert: Access denied
        assert response.status_code in [403, 404], \
            f"Expected 403/404, got {response.status_code}"

    async def test_update_other_org_task_returns_403(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: User A cannot update Organization B's tasks
        Expected: PUT /tasks/{task_b_id} returns 403 or 404
        """
        # Arrange: Create task in Organization B
        org_service = OrganizationService(session)
        team_service = TeamService(session)
        project_service = ProjectService(session)
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

        team_b = await team_service.create_team(
            organization_id=org_b.id,
            name="Team B",
            slug="team-b",
            created_by_user_id=test_users["bob"].id
        )

        project_b = await project_service.create_project(
            organization_id=org_b.id,
            team_id=team_b.id,
            name="Project B",
            slug="project-b",
            created_by_user_id=test_users["bob"].id
        )

        task_b = await task_service.create_task(
            organization_id=org_b.id,
            team_id=team_b.id,
            project_id=project_b.id,
            title="Task B",
            created_by_user_id=test_users["bob"].id
        )

        # Act: User A attempts to update Task B
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        response = await client.put(
            f"/api/v1/tasks/{task_b.id}",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"title": "Hacked Task"}
        )

        # Assert: Update denied
        assert response.status_code in [403, 404], \
            f"Expected 403/404, got {response.status_code}"

        # Assert: Task B remains unchanged
        await session.refresh(task_b)
        assert task_b.title == "Task B", "Task was modified by unauthorized user!"

    async def test_delete_other_org_project_returns_403(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: User A cannot delete Organization B's projects
        Expected: DELETE /projects/{project_b_id} returns 403 or 404
        """
        # Arrange: Create project in Organization B
        org_service = OrganizationService(session)
        team_service = TeamService(session)
        project_service = ProjectService(session)

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

        team_b = await team_service.create_team(
            organization_id=org_b.id,
            name="Team B",
            slug="team-b",
            created_by_user_id=test_users["bob"].id
        )

        project_b = await project_service.create_project(
            organization_id=org_b.id,
            team_id=team_b.id,
            name="Project B",
            slug="project-b",
            created_by_user_id=test_users["bob"].id
        )

        # Act: User A attempts to delete Project B
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        response = await client.delete(
            f"/api/v1/projects/{project_b.id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Assert: Delete denied
        assert response.status_code in [403, 404], \
            f"Expected 403/404, got {response.status_code}"

        # Assert: Project B still exists (not soft-deleted)
        await session.refresh(project_b)
        assert project_b.deleted_at is None, "Project was deleted by unauthorized user!"

    async def test_add_member_to_other_org_returns_403(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: User A cannot add members to Organization B
        Expected: POST /organizations/{org_b_id}/members returns 403
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

        # Act: User A attempts to add Charlie to Organization B
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        response = await client.post(
            f"/api/v1/organizations/{org_b.id}/members",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "user_id": test_users["charlie"].id,
                "role": "member"
            }
        )

        # Assert: Add member denied
        assert response.status_code in [403, 404], \
            f"Expected 403/404, got {response.status_code}"

    async def test_list_operations_filtered_by_organization(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: List operations (GET /tasks, /projects, /teams) return only user's org data
        Expected: Results filtered by organization_id from JWT token
        """
        # Arrange: Create data in both organizations
        org_service = OrganizationService(session)
        team_service = TeamService(session)
        project_service = ProjectService(session)
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

        # Create 2 teams in each org
        for i in range(2):
            await team_service.create_team(
                organization_id=org_a.id,
                name=f"Team A{i+1}",
                slug=f"team-a{i+1}",
                created_by_user_id=test_users["alice"].id
            )

            await team_service.create_team(
                organization_id=org_b.id,
                name=f"Team B{i+1}",
                slug=f"team-b{i+1}",
                created_by_user_id=test_users["bob"].id
            )

        # Act: User A lists teams
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        response = await client.get(
            "/api/v1/teams",
            headers={"Authorization": f"Bearer {token_a}"}
        )

        assert response.status_code == 200
        teams = response.json()

        # Assert: Only Organization A teams returned
        assert len(teams) == 2
        assert all("Team A" in team["name"] for team in teams)
        assert all(team["organization_id"] == str(org_a.id) for team in teams)

    async def test_no_data_leakage_in_error_messages(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_users: dict[str, User]
    ):
        """
        Test: Error messages don't leak information about other organizations
        Expected: Generic "Not Found" or "Forbidden" messages (no details about existence)
        """
        # Arrange: Create Organization B
        org_service = OrganizationService(session)

        org_a = await org_service.create_organization(
            name="Organization A",
            slug="org-a",
            created_by_user_id=test_users["alice"].id
        )

        org_b = await org_service.create_organization(
            name="Organization B - Secret Name",
            slug="org-b-secret",
            created_by_user_id=test_users["bob"].id
        )

        # Act: User A attempts to access Organization B
        from app.core.security import create_access_token

        token_a = create_access_token({
            "sub": test_users["alice"].id,
            "email": test_users["alice"].email,
            "organization_id": str(org_a.id)
        })

        response = await client.get(
            f"/api/v1/organizations/{org_b.id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Assert: Error message doesn't contain organization name
        error_body = response.json()
        error_message = str(error_body.get("detail", "")).lower()

        assert "secret" not in error_message, \
            "Error message leaked organization details!"
        assert "organization b" not in error_message, \
            "Error message leaked organization name!"


@pytest.fixture
async def test_users(session: AsyncSession) -> dict[str, User]:
    """
    Create test users for cross-org access denial tests.

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
