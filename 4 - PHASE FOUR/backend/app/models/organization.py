"""
Organization Model

Top-level tenant boundary in the multi-tenant hierarchy: Organization → Team → Project → Task

References:
- ADR-001: Multi-Tenant Data Isolation Strategy
- Constitution v5.0.0 Principle XIX: Multi-Tenancy & Data Isolation Hierarchy
- specs/005-multi-tenant-collab/data-model.md
"""

from datetime import datetime, UTC
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class Organization(SQLModel, table=True):
    """
    Organization model - top-level tenant boundary.

    Organizations contain teams, which contain projects, which contain tasks.
    All data is scoped to the organization level for multi-tenant isolation.

    Attributes:
        id: Unique organization identifier (UUID)
        name: Organization display name (e.g., "Acme Corp")
        slug: URL-friendly unique identifier (e.g., "acme-corp")
        description: Optional organization description
        created_at: Timestamp when organization was created
        deleted_at: Soft delete timestamp (NULL if active)

    References:
        - ADR-001: Multi-Tenant Data Isolation (application-level filtering)
        - ADR-003: Soft Delete and Audit Trail Strategy
    """

    __tablename__ = "organizations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=255, unique=True, nullable=False, index=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    audit_logs: List["AuditLog"] = Relationship(back_populates="organization")
    teams: List["Team"] = Relationship(back_populates="organization")
    projects: List["Project"] = Relationship(back_populates="organization")
    members: List["OrganizationMember"] = Relationship(back_populates="organization")
    invitations: List["Invitation"] = Relationship(back_populates="organization")

    def __repr__(self) -> str:
        """String representation of Organization."""
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"
