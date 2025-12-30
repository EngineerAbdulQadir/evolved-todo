"""
Team API Schemas

Pydantic models for team request/response validation.

References:
- Task: T078-T085 [US2]
- specs/005-multi-tenant-collab/contracts/teams.yaml
- Constitution v5.0.0 Principle XI: API Design & RESTful Conventions
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Request Schemas

class TeamCreate(BaseModel):
    """Request schema for creating team."""
    name: str = Field(..., min_length=1, max_length=255, description="Team display name")
    description: Optional[str] = Field(None, max_length=1000, description="Optional team description")
    organization_id: UUID = Field(..., description="Parent organization UUID")


class TeamUpdate(BaseModel):
    """Request schema for updating team."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="New team name")
    description: Optional[str] = Field(None, max_length=1000, description="New description")


class TeamMemberAdd(BaseModel):
    """Request schema for adding member to team."""
    user_id: str = Field(..., description="User ID to add as member")
    role: str = Field(..., description="Team role (lead, member)")


# Response Schemas

class TeamResponse(BaseModel):
    """Response schema for team details."""
    id: UUID
    name: str
    description: Optional[str]
    organization_id: UUID
    created_by: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        from_attributes = True


class TeamMemberResponse(BaseModel):
    """Response schema for team member."""
    id: UUID
    team_id: UUID
    user_id: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    """Response schema for list of teams."""
    teams: List[TeamResponse]
    total: int
