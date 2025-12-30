"""
Team API Routes

RESTful endpoints for team CRUD operations with organization scoping and RBAC enforcement.

References:
- Task: T078-T085 [US2]
- specs/005-multi-tenant-collab/contracts/teams.yaml
- ADR-001: Multi-Tenant Data Isolation Strategy
- ADR-002: RBAC Middleware Architecture
- Constitution v5.0.0 Principle XI: API Design & RESTful Conventions
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.middleware.auth import get_current_user_id
from app.models import (
    TeamNotFoundError,
    PermissionDeniedError,
)
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamListResponse,
    TeamMemberAdd,
    TeamMemberResponse,
)
from app.services import TeamService, MemberService


router = APIRouter(prefix="/teams", tags=["teams"])


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create team",
    description="Create a new team within organization (requires org admin or owner role)",
)
async def create_team(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TeamResponse:
    """
    Create a new team.

    User must be organization admin or owner to create teams.

    Args:
        team_data: Team creation data (name, description, organization_id)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        TeamResponse with created team details

    Raises:
        HTTPException 400: If team name already exists in organization
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission (not org admin/owner)

    Task: T078 [US2] - POST /teams (create team, require org admin)
    """
    team_service = TeamService(db)

    try:
        team = await team_service.create_team(
            name=team_data.name,
            description=team_data.description,
            organization_id=team_data.organization_id,
            created_by_user_id=current_user_id,
        )
        return TeamResponse.model_validate(team)
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        # Handle duplicate team name
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team name '{team_data.name}' already exists in organization",
            )
        raise


@router.get(
    "",
    response_model=TeamListResponse,
    summary="List teams",
    description="Get all teams in organization (filtered by organization_id query param)",
)
async def list_teams(
    organization_id: UUID,
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TeamListResponse:
    """
    List teams in organization.

    User must be organization member to view teams.

    Args:
        organization_id: Organization UUID (query parameter)
        include_deleted: Include soft-deleted teams (default: False)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        TeamListResponse with list of teams ordered by created_at DESC

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not organization member

    Task: T079 [US2] - GET /teams (list org's teams)
    """
    team_service = TeamService(db)

    try:
        teams = await team_service.list_teams(
            organization_id=organization_id,
            user_id=current_user_id,
            include_deleted=include_deleted,
        )
        return TeamListResponse(
            teams=[TeamResponse.model_validate(team) for team in teams],
            total=len(teams),
        )
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Get team",
    description="Get team details by ID (requires organization membership)",
)
async def get_team(
    team_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TeamResponse:
    """
    Get team by ID.

    User must be organization member to view team details.

    Args:
        team_id: Team UUID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        TeamResponse with team details

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not organization member
        HTTPException 404: If team not found

    Task: T080 [US2] - GET /teams/{team_id}
    """
    team_service = TeamService(db)

    try:
        team = await team_service.get_team(
            team_id=team_id,
            user_id=current_user_id,
        )
        return TeamResponse.model_validate(team)
    except TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of the organization",
        )


@router.patch(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Update team",
    description="Update team details (requires team lead or org admin/owner role)",
)
async def update_team(
    team_id: UUID,
    team_data: TeamUpdate,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TeamResponse:
    """
    Update team details.

    Only team leads and org admins/owners can update team.

    Args:
        team_id: Team UUID
        team_data: Team update data (name, description)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        TeamResponse with updated team details

    Raises:
        HTTPException 400: If team name already exists
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission (not team lead or org admin)
        HTTPException 404: If team not found

    Task: T081 [US2] - PATCH /teams/{team_id}
    """
    team_service = TeamService(db)

    try:
        team = await team_service.update_team(
            team_id=team_id,
            user_id=current_user_id,
            name=team_data.name,
            description=team_data.description,
        )
        return TeamResponse.model_validate(team)
    except TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        # Handle duplicate team name
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team name already exists in organization",
            )
        raise


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete team",
    description="Soft delete team (requires team lead or org admin/owner role)",
)
async def delete_team(
    team_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    """
    Soft delete team.

    Only team leads and org admins/owners can delete team.
    Sets deleted_at timestamp. Team can be recovered within 30 days.
    Cascades soft delete to projects and tasks.

    Args:
        team_id: Team UUID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission
        HTTPException 404: If team not found

    Task: T082 [US2] - DELETE /teams/{team_id}
    """
    team_service = TeamService(db)

    try:
        await team_service.delete_team(
            team_id=team_id,
            deleted_by_user_id=current_user_id,
        )
    except TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get(
    "/{team_id}/members",
    response_model=List[TeamMemberResponse],
    summary="List team members",
    description="Get all members of team (requires organization membership)",
)
async def list_team_members(
    team_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> List[TeamMemberResponse]:
    """
    List all members of team.

    User must be organization member to view team members.

    Args:
        team_id: Team UUID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        List of TeamMemberResponse ordered by created_at

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not organization member
        HTTPException 404: If team not found

    Task: T083 [US2] - GET /teams/{team_id}/members
    """
    member_service = MemberService(db)

    try:
        members = await member_service.list_team_members(
            team_id=team_id,
            requesting_user_id=current_user_id,
        )
        return [TeamMemberResponse.model_validate(member) for member in members]
    except TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of the organization",
        )


@router.post(
    "/{team_id}/members",
    response_model=TeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add team member",
    description="Add a member to team (requires team lead or org admin/owner role)",
)
async def add_team_member(
    team_id: UUID,
    member_data: TeamMemberAdd,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> TeamMemberResponse:
    """
    Add member to team.

    Only team leads and org admins/owners can add members.
    User must be organization member before joining team.

    Args:
        team_id: Team UUID
        member_data: Member add data (user_id, role)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        TeamMemberResponse with created member details

    Raises:
        HTTPException 400: If user already a team member
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission or target user not org member
        HTTPException 404: If team not found

    Task: T084 [US2] - POST /teams/{team_id}/members
    """
    member_service = MemberService(db)

    try:
        member = await member_service.add_team_member(
            team_id=team_id,
            user_id=member_data.user_id,
            role=member_data.role,
            added_by_user_id=current_user_id,
        )
        return TeamMemberResponse.model_validate(member)
    except TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        # Handle duplicate team member
        if "already a member" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {member_data.user_id} is already a member of team",
            )
        raise


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove team member",
    description="Remove a member from team (requires team lead or org admin/owner role)",
)
async def remove_team_member(
    team_id: UUID,
    user_id: str,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    """
    Remove member from team.

    Only team leads and org admins/owners can remove members.

    Args:
        team_id: Team UUID
        user_id: User ID to remove
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission
        HTTPException 404: If team not found

    Task: T085 [US2] - DELETE /teams/{team_id}/members/{user_id}
    """
    member_service = MemberService(db)

    try:
        await member_service.remove_team_member(
            team_id=team_id,
            user_id=user_id,
            removed_by_user_id=current_user_id,
        )
    except TeamNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
