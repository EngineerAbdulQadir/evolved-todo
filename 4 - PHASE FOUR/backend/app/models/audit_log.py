"""
AuditLog Model

Immutable audit trail for all CRUD operations with 180-day retention.

References:
- ADR-003: Soft Delete and Audit Trail Strategy
- Constitution v5.0.0 Principle XXII: Audit Trails & Change History
- specs/005-multi-tenant-collab/data-model.md
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel


class AuditLog(SQLModel, table=True):
    """
    Audit trail for all CRUD operations.

    Tracks WHO (user_id), WHAT (resource_type, resource_id, action),
    WHEN (created_at), and context for compliance and debugging.

    Task: T171 [US5] - AuditLog model
    ADR-003: Soft Delete and Audit Trail Strategy
    """
    __tablename__ = "audit_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        index=True
    )
    user_id: Optional[UUID] = Field(
        foreign_key="users.id",
        nullable=True,
        index=True
    )  # NULL for system events
    resource_type: str = Field(
        max_length=50,
        nullable=False,
        index=True
    )  # "organization", "team", "project", "task"
    resource_id: UUID = Field(nullable=False, index=True)
    action: str = Field(
        max_length=50,
        nullable=False
    )  # "create", "update", "delete", "add_member", etc.
    context: dict = Field(
        sa_column=Column(JSON),
        default_factory=dict
    )  # JSONB - before/after values, context
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="audit_logs")


class AuditLogCreate(SQLModel):
    """Schema for creating audit log entries."""
    organization_id: UUID
    user_id: Optional[UUID]
    resource_type: str
    resource_id: UUID
    action: str
    context: dict = {}


class AuditLogRead(SQLModel):
    """Schema for reading audit log entries with user details."""
    id: UUID
    organization_id: UUID
    user_id: Optional[UUID]
    resource_type: str
    resource_id: UUID
    action: str
    context: dict
    created_at: datetime
    user_email: Optional[str] = None
