"""
Team Model

Second level in multi-tenant hierarchy: Organization → Team → Project → Task

References:
- ADR-001: Multi-Tenant Data Isolation Strategy
- Constitution v5.0.0 Principle XIX: Multi-Tenancy & Data Isolation Hierarchy
- specs/005-multi-tenant-collab/data-model.md
"""

from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class Team(SQLModel, table=True):
    """
    Team model - functional group within organization.

    Teams represent departments, squads, or functional groups.
    All projects belong to a team, and all tasks belong to projects.

    Attributes:
        id: Unique team identifier (UUID)
        name: Team display name (e.g., "Engineering")
        description: Optional team description
        organization_id: Parent organization UUID
        created_by: User ID who created the team
        created_at: Timestamp when team was created
        updated_at: Timestamp of last update
        deleted_at: Soft delete timestamp (NULL if active)

    Task: T069 [P] [US2] - Team model
    References:
        - ADR-001: Multi-Tenant Data Isolation (application-level filtering)
        - ADR-003: Soft Delete and Audit Trail Strategy
    """

    __tablename__ = "teams"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
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
    organization: "Organization" = Relationship(back_populates="teams")
    members: list["TeamMember"] = Relationship(back_populates="team")
    projects: list["Project"] = Relationship(back_populates="team")

    def __repr__(self) -> str:
        """String representation of Team."""
        return f"<Team(id={self.id}, name={self.name}, org={self.organization_id})>"


class TeamCreate(SQLModel):
    """Schema for creating a team."""
    name: str = Field(max_length=255)
    description: Optional[str] = None
    organization_id: UUID


class TeamRead(SQLModel):
    """Schema for reading team details."""
    id: UUID
    name: str
    description: Optional[str]
    organization_id: UUID
    created_by: str
    created_at: datetime
    member_count: Optional[int] = None
    project_count: Optional[int] = None


class TeamUpdate(SQLModel):
    """Schema for updating team details."""
    name: Optional[str] = None
    description: Optional[str] = None
