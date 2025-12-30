"""
RBAC Permission Definitions and Hierarchies

Defines role enums and permission hierarchies for organization, team, and project levels.

References:
- ADR-002: RBAC Middleware Architecture
- Constitution v5.0.0 Principle XX: Role-Based Access Control
"""

from enum import Enum


class OrganizationRole(str, Enum):
    """
    Organization-level roles with permission inheritance.

    Hierarchy: OWNER > ADMIN > MEMBER
    """
    OWNER = "owner"      # Full control: delete org, manage admins, all team/project access
    ADMIN = "admin"      # Manage teams, invite members, view all teams
    MEMBER = "member"    # View organization, limited team access


class TeamRole(str, Enum):
    """
    Team-level roles with permission inheritance.

    Hierarchy: LEAD > MEMBER
    """
    LEAD = "lead"        # Manage team, create projects, add/remove members
    MEMBER = "member"    # View team, participate in projects


class ProjectRole(str, Enum):
    """
    Project-level roles with permission inheritance.

    Hierarchy: MANAGER > CONTRIBUTOR > VIEWER
    """
    MANAGER = "manager"         # Full project control, manage members, delete project
    CONTRIBUTOR = "contributor"  # Create/edit tasks, assign tasks
    VIEWER = "viewer"            # Read-only access to tasks


# Role hierarchy lookup tables (higher number = more permissions)
ORGANIZATION_ROLE_HIERARCHY = {
    OrganizationRole.OWNER: 3,
    OrganizationRole.ADMIN: 2,
    OrganizationRole.MEMBER: 1,
}

TEAM_ROLE_HIERARCHY = {
    TeamRole.LEAD: 2,
    TeamRole.MEMBER: 1,
}

PROJECT_ROLE_HIERARCHY = {
    ProjectRole.MANAGER: 3,
    ProjectRole.CONTRIBUTOR: 2,
    ProjectRole.VIEWER: 1,
}
