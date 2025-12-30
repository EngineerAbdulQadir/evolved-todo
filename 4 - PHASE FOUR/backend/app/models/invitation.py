"""
Invitation Model

Secure invitation system for onboarding users to organizations, teams, and projects.

References:
- ADR-004: Invitation System Security Design
- Constitution v5.0.0 Principle XXIII: Invitation System & User Onboarding
- specs/005-multi-tenant-collab/data-model.md
"""

from datetime import datetime, UTC
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class Invitation(SQLModel, table=True):
    """
    Invitation model for secure user onboarding.

    Supports invitations to organizations, teams, and projects with role assignment.
    Tokens are cryptographically secure (256-bit) with 7-day expiration and one-time use.

    Attributes:
        id: Unique invitation identifier (UUID)
        organization_id: Organization to invite user to (FK, required)
        team_id: Optional team to invite user to (FK, nullable)
        project_id: Optional project to invite user to (FK, nullable)
        email: Invitee's email address
        role: Role to assign on acceptance (owner, admin, member, lead, manager, contributor, viewer)
        token: Cryptographically secure 256-bit token (unique, urlsafe)
        invited_by: User who created the invitation (FK)
        accepted_at: Timestamp when invitation was accepted (NULL if pending)
        accepted_by: User who accepted the invitation (FK, NULL if pending)
        expires_at: Expiration timestamp (created_at + 7 days)
        created_at: Timestamp when invitation was created

    References:
        - ADR-004: Invitation System Security Design (256-bit tokens, 7-day expiration, one-time use)
    """

    __tablename__ = "invitations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id", nullable=False, index=True)
    team_id: Optional[UUID] = Field(default=None, foreign_key="teams.id", nullable=True)
    project_id: Optional[UUID] = Field(default=None, foreign_key="projects.id", nullable=True)
    email: str = Field(max_length=255, nullable=False, index=True)
    role: str = Field(max_length=50, nullable=False)
    token: str = Field(max_length=255, unique=True, nullable=False, index=True)
    invited_by: str = Field(foreign_key="user.id", max_length=255, nullable=False)
    accepted_at: Optional[datetime] = Field(default=None, nullable=True, index=True)
    accepted_by: Optional[str] = Field(default=None, foreign_key="user.id", max_length=255, nullable=True)
    expires_at: datetime = Field(nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    organization: "Organization" = Relationship(back_populates="invitations")

    def __repr__(self) -> str:
        """String representation of Invitation."""
        status = "accepted" if self.accepted_at else "pending"
        return f"<Invitation(id={self.id}, email={self.email}, status={status}, expires={self.expires_at})>"

    @property
    def is_expired(self) -> bool:
        """Check if invitation has expired."""
        return datetime.now(UTC) > self.expires_at

    @property
    def is_accepted(self) -> bool:
        """Check if invitation has been accepted."""
        return self.accepted_at is not None
