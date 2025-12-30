"""
OrganizationMember Model (Join Table)

Represents membership relationship between User and Organization with role assignment.

References:
- ADR-002: RBAC Middleware Architecture
- Constitution v5.0.0 Principle XX: Role-Based Access Control
- specs/005-multi-tenant-collab/data-model.md
"""

from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


class OrganizationMember(SQLModel, table=True):
    """
    OrganizationMember join table - User ↔ Organization membership with role.

    Each record represents a user's membership in an organization with an assigned role.
    Unique constraint ensures a user can only be a member of an organization once.

    Attributes:
        id: Unique membership identifier (UUID)
        organization_id: Organization this membership belongs to (FK)
        user_id: User who is a member (FK)
        role: User's role in the organization (owner, admin, member)
        created_at: Timestamp when membership was created

    References:
        - ADR-002: RBAC Middleware Architecture
        - Constitution v5.0.0 Principle XX: Role-Based Access Control
    """

    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member"),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id", nullable=False, index=True)
    user_id: str = Field(foreign_key="user.id", max_length=255, nullable=False, index=True)
    role: str = Field(max_length=50, nullable=False)  # OrganizationRole enum value
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    organization: "Organization" = Relationship(back_populates="members")

    def __repr__(self) -> str:
        """String representation of OrganizationMember."""
        return f"<OrganizationMember(org_id={self.organization_id}, user_id={self.user_id}, role={self.role})>"
