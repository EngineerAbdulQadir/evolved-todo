"""
Custom Exceptions for Multi-Tenant Application

Business logic exceptions for organization, invitation, and RBAC operations.

References:
- Constitution v5.0.0 Principle IV: Error Handling & Observability
- specs/005-multi-tenant-collab/plan.md § Error Handling
"""


class MultiTenantBaseException(Exception):
    """Base exception for multi-tenant application errors."""
    pass


# Organization Exceptions
class OrganizationNotFoundError(MultiTenantBaseException):
    """Raised when organization is not found or user lacks access."""
    def __init__(self, org_id: str):
        self.org_id = org_id
        super().__init__(f"Organization {org_id} not found or access denied")


class DuplicateSlugError(MultiTenantBaseException):
    """Raised when attempting to create organization with duplicate slug."""
    def __init__(self, slug: str):
        self.slug = slug
        super().__init__(f"Organization slug '{slug}' already exists")


# Permission Exceptions
class PermissionDeniedError(MultiTenantBaseException):
    """Raised when user lacks required permissions for operation."""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message)


# Invitation Exceptions
class InvitationNotFoundError(MultiTenantBaseException):
    """Raised when invitation is not found."""
    def __init__(self, token_or_id: str):
        super().__init__(f"Invitation not found: {token_or_id}")


class InvitationExpiredError(MultiTenantBaseException):
    """Raised when attempting to accept expired invitation."""
    def __init__(self):
        super().__init__("Invitation has expired")


class InvitationAlreadyAcceptedError(MultiTenantBaseException):
    """Raised when attempting to accept already-accepted invitation."""
    def __init__(self):
        super().__init__("Invitation has already been accepted")


# Team Exceptions
class TeamNotFoundError(MultiTenantBaseException):
    """Raised when team is not found or user lacks access."""
    def __init__(self, team_id: str):
        self.team_id = team_id
        super().__init__(f"Team {team_id} not found or access denied")


# Project Exceptions
class ProjectNotFoundError(MultiTenantBaseException):
    """Raised when project is not found or user lacks access."""
    def __init__(self, project_id: str):
        self.project_id = project_id
        super().__init__(f"Project {project_id} not found or access denied")


# Task Exceptions
class TaskNotFoundError(MultiTenantBaseException):
    """Raised when task is not found or user lacks access."""
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found or access denied")
