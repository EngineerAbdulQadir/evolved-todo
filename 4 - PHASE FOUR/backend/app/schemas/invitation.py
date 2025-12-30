"""
Invitation API Schemas

Pydantic models for invitation request/response validation.

References:
- Task: T043-T053 [P] [US1]
- specs/005-multi-tenant-collab/contracts/invitations.yaml
- ADR-004: Invitation System Security Design
- Constitution v5.0.0 Principle XI: API Design & RESTful Conventions
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


# Request Schemas

class InvitationCreate(BaseModel):
    """Request schema for creating invitation."""
    organization_id: UUID = Field(..., description="Organization to invite user to")
    team_id: Optional[UUID] = Field(None, description="Optional team to invite user to")
    project_id: Optional[UUID] = Field(None, description="Optional project to invite user to")
    email: EmailStr = Field(..., description="Invitee's email address")
    role: str = Field(..., description="Role to assign on acceptance")


class InvitationAccept(BaseModel):
    """Request schema for accepting invitation (optional, can be empty)."""
    pass


# Response Schemas

class InvitationResponse(BaseModel):
    """Response schema for invitation details."""
    id: UUID
    organization_id: UUID
    team_id: Optional[UUID]
    project_id: Optional[UUID]
    email: str
    role: str
    token: str
    invited_by: str
    accepted_at: Optional[datetime]
    accepted_by: Optional[str]
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class InvitationListResponse(BaseModel):
    """Response schema for list of invitations."""
    invitations: List[InvitationResponse]
    total: int


class InvitationAcceptResponse(BaseModel):
    """Response schema for invitation acceptance."""
    message: str
    organization_id: UUID
