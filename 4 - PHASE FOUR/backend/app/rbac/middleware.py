"""
RBAC Middleware - FastAPI Dependency Factories

Provides dependency factories for enforcing RBAC permissions at organization, team, and project levels.

References:
- ADR-002: RBAC Middleware Architecture (FastAPI dependency injection pattern)
- Constitution v5.0.0 Principle XX: Role-Based Access Control
"""

from typing import Callable

from fastapi import Depends, HTTPException

from app.rbac.context import TenantContext, get_tenant_context
from app.rbac.permissions import (
    OrganizationRole,
    TeamRole,
    ProjectRole,
    ORGANIZATION_ROLE_HIERARCHY,
    TEAM_ROLE_HIERARCHY,
    PROJECT_ROLE_HIERARCHY
)


def require_org_role(required_role: OrganizationRole) -> Callable:
    """
    FastAPI dependency factory for enforcing organization-level permissions.

    Args:
        required_role: Minimum required organization role (owner, admin, member)

    Returns:
        Async dependency function that validates user has required org role

    Raises:
        HTTPException: 403 if user doesn't have required organization role

    Example:
        @router.post("/organizations/{org_id}/teams")
        async def create_team(
            org_id: UUID,
            tenant_context: TenantContext = Depends(require_org_role(OrganizationRole.ADMIN))
        ):
            # Only org admins/owners can create teams
            pass

    References:
        - ADR-002: RBAC Middleware Architecture
        - Constitution v5.0.0 Principle XX: Role-Based Access Control
    """
    async def dependency(
        tenant_context: TenantContext = Depends(get_tenant_context)
    ) -> TenantContext:
        # Organization owners have full access (bypass hierarchy check)
        if tenant_context.org_role == OrganizationRole.OWNER.value:
            return tenant_context

        # Check role hierarchy (higher number = more permissions)
        current_role_level = ORGANIZATION_ROLE_HIERARCHY.get(
            OrganizationRole(tenant_context.org_role),
            0
        )
        required_role_level = ORGANIZATION_ROLE_HIERARCHY.get(required_role, 999)

        if current_role_level < required_role_level:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient organization permissions. Requires {required_role.value} or higher. "
                       f"Current role: {tenant_context.org_role}"
            )

        return tenant_context

    return dependency


def require_team_role(required_role: TeamRole) -> Callable:
    """
    FastAPI dependency factory for enforcing team-level permissions.

    Organization owners bypass team role checks (permission inheritance).

    Args:
        required_role: Minimum required team role (lead, member)

    Returns:
        Async dependency function that validates user has required team role

    Raises:
        HTTPException: 403 if user doesn't have required team role

    Example:
        @router.post("/teams/{team_id}/projects")
        async def create_project(
            team_id: UUID,
            tenant_context: TenantContext = Depends(require_team_role(TeamRole.LEAD))
        ):
            # Only team leads or org owners can create projects
            pass

    References:
        - ADR-002: RBAC Middleware Architecture (permission inheritance)
    """
    async def dependency(
        tenant_context: TenantContext = Depends(get_tenant_context)
    ) -> TenantContext:
        # Organization owners bypass team checks (permission inheritance)
        if tenant_context.org_role == OrganizationRole.OWNER.value:
            return tenant_context

        # Organization admins have team lead permissions
        if tenant_context.org_role == OrganizationRole.ADMIN.value:
            return tenant_context

        # Validate team role
        if not tenant_context.team_role:
            raise HTTPException(
                status_code=403,
                detail="No team context in JWT. Please switch to a team using /auth/switch-context"
            )

        # Check team role hierarchy
        current_role_level = TEAM_ROLE_HIERARCHY.get(
            TeamRole(tenant_context.team_role),
            0
        )
        required_role_level = TEAM_ROLE_HIERARCHY.get(required_role, 999)

        if current_role_level < required_role_level:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient team permissions. Requires {required_role.value} or higher. "
                       f"Current role: {tenant_context.team_role}"
            )

        return tenant_context

    return dependency


def require_project_role(required_role: ProjectRole) -> Callable:
    """
    FastAPI dependency factory for enforcing project-level permissions.

    Organization owners and team leads bypass project role checks (permission inheritance).

    Args:
        required_role: Minimum required project role (manager, contributor, viewer)

    Returns:
        Async dependency function that validates user has required project role

    Raises:
        HTTPException: 403 if user doesn't have required project role

    Example:
        @router.patch("/projects/{project_id}/tasks/{task_id}")
        async def update_task(
            project_id: UUID,
            task_id: UUID,
            tenant_context: TenantContext = Depends(require_project_role(ProjectRole.CONTRIBUTOR))
        ):
            # Contributors, managers, team leads, or org owners can update tasks
            pass

    References:
        - ADR-002: RBAC Middleware Architecture (permission inheritance)
    """
    async def dependency(
        tenant_context: TenantContext = Depends(get_tenant_context)
    ) -> TenantContext:
        # Organization owners bypass project checks (permission inheritance)
        if tenant_context.org_role == OrganizationRole.OWNER.value:
            return tenant_context

        # Team leads bypass project checks (permission inheritance)
        if tenant_context.team_role and tenant_context.team_role == TeamRole.LEAD.value:
            return tenant_context

        # Validate project role
        if not tenant_context.project_role:
            raise HTTPException(
                status_code=403,
                detail="No project context in JWT. Please switch to a project using /auth/switch-context"
            )

        # Check project role hierarchy
        current_role_level = PROJECT_ROLE_HIERARCHY.get(
            ProjectRole(tenant_context.project_role),
            0
        )
        required_role_level = PROJECT_ROLE_HIERARCHY.get(required_role, 999)

        if current_role_level < required_role_level:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient project permissions. Requires {required_role.value} or higher. "
                       f"Current role: {tenant_context.project_role}"
            )

        return tenant_context

    return dependency
