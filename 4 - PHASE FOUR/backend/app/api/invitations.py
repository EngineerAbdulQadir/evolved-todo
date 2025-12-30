"""
Invitation API Routes

RESTful endpoints for invitation management with secure token handling.

References:
- Task: T049-T053 [P] [US1]
- specs/005-multi-tenant-collab/contracts/invitations.yaml
- ADR-004: Invitation System Security Design
- Constitution v5.0.0 Principle XXIII: Invitation System & User Onboarding
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.middleware.auth import get_current_user_id
from app.models import (
    InvitationNotFoundError,
    InvitationExpiredError,
    InvitationAlreadyAcceptedError,
    PermissionDeniedError,
)
from app.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationListResponse,
    InvitationAcceptResponse,
)
from app.services import InvitationService


router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post(
    "",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create invitation",
    description="Create a new invitation with secure 256-bit token",
)
async def create_invitation(
    invitation_data: InvitationCreate,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> InvitationResponse:
    """
    Create a new invitation.

    Generates cryptographically secure 256-bit token with 7-day expiration.
    Inviting user must be a member of the organization.

    Args:
        invitation_data: Invitation creation data (org_id, email, role, team_id, project_id)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        InvitationResponse with invitation details including secure token

    Raises:
        HTTPException 400: If email format invalid
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not a member of organization
    """
    invitation_service = InvitationService(db)

    try:
        invitation = await invitation_service.create_invitation(
            organization_id=invitation_data.organization_id,
            team_id=invitation_data.team_id,
            project_id=invitation_data.project_id,
            email=invitation_data.email,
            role=invitation_data.role,
            invited_by_user_id=current_user_id,
        )
        return InvitationResponse.model_validate(invitation)
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get(
    "/token/{token}",
    response_model=InvitationResponse,
    summary="Get invitation by token",
    description="Get invitation details by token (public endpoint for acceptance flow)",
)
async def get_invitation_by_token(
    token: str,
    db: AsyncSession = Depends(get_session),
) -> InvitationResponse:
    """
    Get invitation by token.

    Public endpoint - no authentication required.
    Used in invitation acceptance flow to display invitation details.

    Args:
        token: Invitation token
        db: Database session

    Returns:
        InvitationResponse with invitation details

    Raises:
        HTTPException 404: If token not found
    """
    invitation_service = InvitationService(db)

    try:
        invitation = await invitation_service.get_invitation_by_token(token=token)
        return InvitationResponse.model_validate(invitation)
    except InvitationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )


@router.post(
    "/{token}/accept",
    response_model=InvitationAcceptResponse,
    summary="Accept invitation",
    description="Accept invitation and add user to organization",
)
async def accept_invitation(
    token: str,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> InvitationAcceptResponse:
    """
    Accept invitation.

    Validates token, expiration, and one-time use.
    Adds user to organization with specified role.
    Marks invitation as accepted.

    Args:
        token: Invitation token
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        InvitationAcceptResponse with success message and organization ID

    Raises:
        HTTPException 400: If invitation expired or already accepted
        HTTPException 401: If unauthenticated
        HTTPException 404: If token not found
    """
    invitation_service = InvitationService(db)

    try:
        org = await invitation_service.accept_invitation(
            token=token,
            accepting_user_id=current_user_id,
        )
        return InvitationAcceptResponse(
            message="Invitation accepted successfully",
            organization_id=org.id,
        )
    except InvitationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )
    except InvitationExpiredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired",
        )
    except InvitationAlreadyAcceptedError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has already been accepted",
        )


@router.delete(
    "/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke invitation",
    description="Revoke (delete) invitation",
)
async def revoke_invitation(
    invitation_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    """
    Revoke invitation.

    Deletes invitation from database.
    Revoking user must be a member of the organization.

    Args:
        invitation_id: Invitation UUID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not a member of organization
        HTTPException 404: If invitation not found
    """
    invitation_service = InvitationService(db)

    try:
        await invitation_service.revoke_invitation(
            invitation_id=invitation_id,
            revoked_by_user_id=current_user_id,
        )
    except InvitationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get(
    "/organizations/{org_id}",
    response_model=InvitationListResponse,
    summary="List invitations",
    description="List all invitations for organization (pending, accepted, expired)",
)
async def list_invitations(
    org_id: UUID,
    include_accepted: bool = False,
    include_expired: bool = False,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> InvitationListResponse:
    """
    List invitations for organization (all states).

    Task: T190 [US7] - Update GET /invitations to show all states

    By default, returns only pending (unaccepted, non-expired) invitations.
    Use query parameters to include accepted or expired invitations.

    Args:
        org_id: Organization UUID
        include_accepted: Whether to include accepted invitations (default: False)
        include_expired: Whether to include expired invitations (default: False)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        InvitationListResponse with list of invitations matching filters

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not a member of organization

    Examples:
        - GET /invitations/organizations/{org_id} → pending only
        - GET /invitations/organizations/{org_id}?include_accepted=true → pending + accepted
        - GET /invitations/organizations/{org_id}?include_expired=true → pending + expired
        - GET /invitations/organizations/{org_id}?include_accepted=true&include_expired=true → all
    """
    invitation_service = InvitationService(db)

    try:
        invitations = await invitation_service.list_invitations(
            organization_id=org_id,
            requesting_user_id=current_user_id,
            include_accepted=include_accepted,
            include_expired=include_expired,
        )
        return InvitationListResponse(
            invitations=[InvitationResponse.model_validate(inv) for inv in invitations],
            total=len(invitations),
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
