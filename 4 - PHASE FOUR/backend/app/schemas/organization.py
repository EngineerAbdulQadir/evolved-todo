"""
Organization API Schemas

Pydantic models for organization request/response validation.

References:
- Task: T043-T053 [P] [US1]
- specs/005-multi-tenant-collab/contracts/organizations.yaml
- Constitution v5.0.0 Principle XI: API Design & RESTful Conventions
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


# Request Schemas

class OrganizationCreate(BaseModel):
    """Request schema for creating organization."""
    name: str = Field(..., min_length=1, max_length=255, description="Organization display name")
    slug: str = Field(..., min_length=1, max_length=255, description="URL-friendly unique identifier")
    description: Optional[str] = Field(None, description="Optional organization description")


class OrganizationUpdate(BaseModel):
    """Request schema for updating organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="New organization name")
    slug: Optional[str] = Field(None, min_length=1, max_length=255, description="New slug")
    description: Optional[str] = Field(None, description="New description")


class MemberAdd(BaseModel):
    """Request schema for adding member to organization."""
    user_id: str = Field(..., description="User ID to add as member")
    role: str = Field(..., description="Role to assign (owner, admin, member)")


# Response Schemas

class OrganizationResponse(BaseModel):
    """Response schema for organization details."""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    created_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True


class OrganizationMemberResponse(BaseModel):
    """Response schema for organization member."""
    id: UUID
    organization_id: UUID
    user_id: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationListResponse(BaseModel):
    """Response schema for list of organizations."""
    organizations: List[OrganizationResponse]
    total: int
