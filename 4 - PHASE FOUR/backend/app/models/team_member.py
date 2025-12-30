"""
TeamMember Model (Join Table)

Represents membership relationship between User and Team with role assignment.

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


class TeamRole(str, Enum):
    """Team role enumeration for RBAC."""
    LEAD = "lead"
    MEMBER = "member"


class TeamMember(SQLModel, table=True):
    """
    TeamMember model - user-to-team membership with role.

    Links users to teams with role assignment (Lead, Member).
    User must be an organization member before joining a team.

    Attributes:
        id: Unique team member identifier (UUID)
        team_id: Team UUID
        user_id: User UUID
        role: Team role (lead or member)
        created_at: Timestamp when membership was created
        updated_at: Timestamp of last update

    Task: T070 [P] [US2] - TeamMember model
    References:
        - ADR-002: RBAC Middleware Architecture
        - specs/005-multi-tenant-collab/data-model.md
    """

    __tablename__ = "team_members"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    team_id: UUID = Field(
        foreign_key="teams.id",
        nullable=False,
        index=True
    )
    user_id: str = Field(nullable=False, index=True)  # User ID
    role: str = Field(nullable=False)  # TeamRole value
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    team: "Team" = Relationship(back_populates="members")

    def __repr__(self) -> str:
        """String representation of TeamMember."""
        return f"<TeamMember(team={self.team_id}, user={self.user_id}, role={self.role})>"


class TeamMemberCreate(SQLModel):
    """Schema for creating team member."""
    team_id: UUID
    user_id: str
    role: str  # TeamRole value


class TeamMemberRead(SQLModel):
    """Schema for reading team member details."""
    id: UUID
    team_id: UUID
    user_id: str
    role: str
    created_at: datetime
    user_email: Optional[str] = None
    user_name: Optional[str] = None
