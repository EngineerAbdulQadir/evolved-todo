"""
RBAC (Role-Based Access Control) Module

This module provides FastAPI dependency injection for multi-tenant RBAC.

Components:
- permissions.py: Role definitions and permission hierarchies
- middleware.py: RBAC dependency factories (require_org_role, require_team_role, require_project_role)
- context.py: Tenant context extraction from JWT tokens

References:
- ADR-002: RBAC Middleware Architecture (FastAPI dependency injection)
- Constitution v5.0.0 Principle XX: Role-Based Access Control (RBAC)
"""

from app.rbac.context import TenantContext, get_current_user, get_tenant_context
from app.rbac.middleware import require_org_role, require_project_role, require_team_role
from app.rbac.permissions import (
    OrganizationRole,
    ProjectRole,
    TeamRole,
    ORGANIZATION_ROLE_HIERARCHY,
    PROJECT_ROLE_HIERARCHY,
    TEAM_ROLE_HIERARCHY,
)

__all__ = [
    # Context
    "TenantContext",
    "get_current_user",
    "get_tenant_context",
    # Middleware
    "require_org_role",
    "require_team_role",
    "require_project_role",
    # Permissions
    "OrganizationRole",
    "TeamRole",
    "ProjectRole",
    "ORGANIZATION_ROLE_HIERARCHY",
    "TEAM_ROLE_HIERARCHY",
    "PROJECT_ROLE_HIERARCHY",
]
