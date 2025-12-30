"""
ProjectMember Model (Join Table)

Represents membership relationship between User and Project with role assignment.

References:
- ADR-002: RBAC Middleware Architecture
- Constitution v5.0.0 Principle XX: Role-Based Access Control
- specs/005-multi-tenant-collab/data-model.md
"""

from datetime import datetime, UTC
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class ProjectRole(str, Enum):
    """Project role enumeration for RBAC."""
    MANAGER = "manager"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"


class ProjectMember(SQLModel, table=True):
    """
    ProjectMember model - user-to-project membership with role.

    Links users to projects with role assignment (Manager, Contributor, Viewer).
    User must be a team member before joining a project.

    Attributes:
        id: Unique project member identifier (UUID)
        project_id: Project UUID
        user_id: User UUID
        role: Project role (manager, contributor, or viewer)
        created_at: Timestamp when membership was created
        updated_at: Timestamp of last update

    Task: T099 [P] [US3] - ProjectMember model
    References:
        - ADR-002: RBAC Middleware Architecture
        - specs/005-multi-tenant-collab/data-model.md
    """

    __tablename__ = "project_members"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    project_id: UUID = Field(
        foreign_key="projects.id",
        nullable=False,
        index=True
    )
    user_id: str = Field(nullable=False, index=True)  # User ID
    role: str = Field(nullable=False)  # ProjectRole value
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    project: "Project" = Relationship(back_populates="members")

    def __repr__(self) -> str:
        """String representation of ProjectMember."""
        return f"<ProjectMember(project={self.project_id}, user={self.user_id}, role={self.role})>"


class ProjectMemberCreate(SQLModel):
    """Schema for creating project member."""
    project_id: UUID
    user_id: str
    role: str  # ProjectRole value


class ProjectMemberRead(SQLModel):
    """Schema for reading project member details."""
    id: UUID
    project_id: UUID
    user_id: str
    role: str
    created_at: datetime
    user_email: Optional[str] = None
    user_name: Optional[str] = None
