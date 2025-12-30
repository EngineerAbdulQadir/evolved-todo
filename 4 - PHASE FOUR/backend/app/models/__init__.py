"""
SQLModel database models.

This module exports all database models for the application.
Phase 2: User, Task, Account, Session
Phase 3: Conversation, Message (AI Chatbot)
Phase 3.1: Organization, OrganizationMember, Invitation (Multi-Tenant) - NEW
"""

from sqlmodel import SQLModel

from .audit_log import AuditLog, AuditLogCreate, AuditLogRead
from .conversation import Conversation
from .exceptions import (
    DuplicateSlugError,
    InvitationAlreadyAcceptedError,
    InvitationExpiredError,
    InvitationNotFoundError,
    MultiTenantBaseException,
    OrganizationNotFoundError,
    PermissionDeniedError,
    ProjectNotFoundError,
    TaskNotFoundError,
    TeamNotFoundError,
)
from .invitation import Invitation
from .message import Message, MessageRole
from .organization import Organization
from .organization_member import OrganizationMember
from .project import Project
from .project_member import ProjectMember
from .task import Priority, RecurrencePattern, Task
from .team import Team
from .team_member import TeamMember
from .user import Account, Session, User

__all__ = [
    "SQLModel",
    "User",
    "Account",
    "Session",
    "Task",
    "Priority",
    "RecurrencePattern",
    "Conversation",
    "Message",
    "MessageRole",
    "Organization",
    "OrganizationMember",
    "Team",
    "TeamMember",
    "Project",
    "ProjectMember",
    "Invitation",
    "AuditLog",
    "AuditLogCreate",
    "AuditLogRead",
    # Exceptions
    "MultiTenantBaseException",
    "OrganizationNotFoundError",
    "DuplicateSlugError",
    "PermissionDeniedError",
    "InvitationNotFoundError",
    "InvitationExpiredError",
    "InvitationAlreadyAcceptedError",
    "TeamNotFoundError",
    "ProjectNotFoundError",
    "TaskNotFoundError",
]
