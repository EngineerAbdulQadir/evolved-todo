"""
Project Model

Third level in multi-tenant hierarchy: Organization → Team → Project → Task

References:
- ADR-001: Multi-Tenant Data Isolation Strategy
- Constitution v5.0.0 Principle XIX: Multi-Tenancy & Data Isolation Hierarchy
- specs/005-multi-tenant-collab/data-model.md
"""

from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class Project(SQLModel, table=True):
    """
    Project model - container for tasks within a team.

    Projects organize work within teams. All tasks belong to a project.
    Projects inherit access from team membership.

    Attributes:
        id: Unique project identifier (UUID)
        name: Project display name (e.g., "Q1 2025 Launch")
        description: Optional project description
        team_id: Parent team UUID
        organization_id: Parent organization UUID (denormalized for filtering)
        created_by: User ID who created the project
        created_at: Timestamp when project was created
        updated_at: Timestamp of last update
        deleted_at: Soft delete timestamp (NULL if active)

    Task: T098 [P] [US3] - Project model
    References:
        - ADR-001: Multi-Tenant Data Isolation (application-level filtering)
        - ADR-003: Soft Delete and Audit Trail Strategy
    """

    __tablename__ = "projects"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    team_id: UUID = Field(
        foreign_key="teams.id",
        nullable=False,
        index=True
    )
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        index=True
    )
    created_by: str = Field(nullable=False)  # User ID
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    team: "Team" = Relationship(back_populates="projects")
    organization: "Organization" = Relationship(back_populates="projects")
    members: list["ProjectMember"] = Relationship(back_populates="project")
    tasks: list["Task"] = Relationship(back_populates="project")

    def __repr__(self) -> str:
        """String representation of Project."""
        return f"<Project(id={self.id}, name={self.name}, team={self.team_id})>"


class ProjectCreate(SQLModel):
    """Schema for creating a project."""
    name: str = Field(max_length=255)
    description: Optional[str] = None
    team_id: UUID


class ProjectRead(SQLModel):
    """Schema for reading project details."""
    id: UUID
    name: str
    description: Optional[str]
    team_id: UUID
    organization_id: UUID
    created_by: str
    created_at: datetime
    member_count: Optional[int] = None
    task_count: Optional[int] = None


class ProjectUpdate(SQLModel):
    """Schema for updating project details."""
    name: Optional[str] = None
    description: Optional[str] = None
