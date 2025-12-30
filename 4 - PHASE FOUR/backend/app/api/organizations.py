"""
Organization API Routes

RESTful endpoints for organization CRUD operations with RBAC enforcement.

References:
- Task: T043-T048 [P] [US1]
- specs/005-multi-tenant-collab/contracts/organizations.yaml
- ADR-002: RBAC Middleware Architecture
- Constitution v5.0.0 Principle XI: API Design & RESTful Conventions
"""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

logger = logging.getLogger(__name__)

from app.core.database import get_session
from app.middleware.auth import get_current_user_id
from app.models import (
    DuplicateSlugError,
    OrganizationNotFoundError,
    PermissionDeniedError,
)
from app.schemas.organization import (
    MemberAdd,
    OrganizationCreate,
    OrganizationListResponse,
    OrganizationMemberResponse,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services import OrganizationService


router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
    description="Create a new organization with the authenticated user as owner",
)
async def create_organization(
    org_data: OrganizationCreate,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> OrganizationResponse:
    """
    Create a new organization.

    Creator is automatically added as OWNER.

    Args:
        org_data: Organization creation data (name, slug, description)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        OrganizationResponse with created organization details

    Raises:
        HTTPException 400: If slug already exists
        HTTPException 401: If unauthenticated
    """
    logger.info(f"[DEBUG] create_organization called: user_id={current_user_id}, org_data={org_data}")
    org_service = OrganizationService(db)

    try:
        org = await org_service.create_organization(
            name=org_data.name,
            slug=org_data.slug,
            description=org_data.description,
            created_by_user_id=current_user_id,
        )
        logger.info(f"[DEBUG] Organization created successfully: {org.id}")
        return OrganizationResponse.model_validate(org)
    except DuplicateSlugError as e:
        logger.error(f"[DEBUG] DuplicateSlugError: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization slug '{e.slug}' already exists",
        )
    except Exception as e:
        logger.error(f"[DEBUG] Unexpected error: {type(e).__name__}: {e}", exc_info=True)
        raise


@router.get(
    "",
    response_model=OrganizationListResponse,
    summary="List organizations",
    description="Get all organizations the authenticated user is a member of",
)
async def list_organizations(
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> OrganizationListResponse:
    """
    List organizations user is a member of.

    Args:
        include_deleted: Include soft-deleted organizations (default: False)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        OrganizationListResponse with list of organizations ordered by created_at DESC

    Raises:
        HTTPException 401: If unauthenticated
    """
    org_service = OrganizationService(db)

    orgs = await org_service.list_organizations(
        user_id=current_user_id,
        include_deleted=include_deleted,
    )

    return OrganizationListResponse(
        organizations=[OrganizationResponse.model_validate(org) for org in orgs],
        total=len(orgs),
    )


@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Get organization",
    description="Get organization details by ID (requires membership)",
)
async def get_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> OrganizationResponse:
    """
    Get organization by ID.

    User must be a member to access organization details.

    Args:
        org_id: Organization UUID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        OrganizationResponse with organization details

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not a member
        HTTPException 404: If organization not found
    """
    org_service = OrganizationService(db)

    try:
        org = await org_service.get_organization(
            organization_id=org_id,
            user_id=current_user_id,
        )
        return OrganizationResponse.model_validate(org)
    except OrganizationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found",
        )
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )


@router.get(
    "/slug/{slug}",
    response_model=OrganizationResponse,
    summary="Get organization by slug",
    description="Get organization details by slug (requires membership)",
)
async def get_organization_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> OrganizationResponse:
    """
    Get organization by slug.

    User must be a member to access organization details.

    Args:
        slug: Organization slug
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        OrganizationResponse with organization details

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not a member
        HTTPException 404: If organization not found
    """
    org_service = OrganizationService(db)

    try:
        org = await org_service.get_organization_by_slug(
            slug=slug,
            user_id=current_user_id,
        )
        return OrganizationResponse.model_validate(org)
    except OrganizationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with slug '{slug}' not found",
        )
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )


@router.patch(
    "/{org_id}",
    response_model=OrganizationResponse,
    summary="Update organization",
    description="Update organization details (requires owner or admin role)",
)
async def update_organization(
    org_id: UUID,
    org_data: OrganizationUpdate,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> OrganizationResponse:
    """
    Update organization details.

    Only owners and admins can update organization.

    Args:
        org_id: Organization UUID
        org_data: Organization update data (name, slug, description)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        OrganizationResponse with updated organization details

    Raises:
        HTTPException 400: If slug already exists
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission
        HTTPException 404: If organization not found
    """
    org_service = OrganizationService(db)

    try:
        org = await org_service.update_organization(
            organization_id=org_id,
            user_id=current_user_id,
            name=org_data.name,
            description=org_data.description,
            slug=org_data.slug,
        )
        return OrganizationResponse.model_validate(org)
    except OrganizationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except DuplicateSlugError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization slug '{e.slug}' already exists",
        )


@router.delete(
    "/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete organization",
    description="Soft delete organization (requires owner role)",
)
async def delete_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    """
    Soft delete organization.

    Only owners can delete organization. Sets deleted_at timestamp.
    Organization can be recovered within 30 days.

    Args:
        org_id: Organization UUID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not owner
        HTTPException 404: If organization not found
    """
    org_service = OrganizationService(db)

    try:
        await org_service.soft_delete_organization(
            organization_id=org_id,
            deleted_by_user_id=current_user_id,
        )
    except OrganizationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {org_id} not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get(
    "/{org_id}/members",
    response_model=List[OrganizationMemberResponse],
    summary="List organization members",
    description="Get all members of organization (requires membership)",
)
async def list_members(
    org_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> List[OrganizationMemberResponse]:
    """
    List all members of organization.

    User must be a member to view member list.

    Args:
        org_id: Organization UUID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        List of OrganizationMemberResponse ordered by created_at

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not a member
        HTTPException 404: If organization not found
    """
    org_service = OrganizationService(db)

    try:
        members = await org_service.list_members(
            organization_id=org_id,
            requesting_user_id=current_user_id,
        )
        return [OrganizationMemberResponse.model_validate(member) for member in members]
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )


@router.post(
    "/{org_id}/members",
    response_model=OrganizationMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add organization member",
    description="Add a member to organization (requires owner or admin role)",
)
async def add_member(
    org_id: UUID,
    member_data: MemberAdd,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> OrganizationMemberResponse:
    """
    Add member to organization.

    Only owners and admins can add members.

    Args:
        org_id: Organization UUID
        member_data: Member add data (user_id, role)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        OrganizationMemberResponse with created member details

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission
        HTTPException 404: If organization not found
    """
    org_service = OrganizationService(db)

    try:
        member = await org_service.add_member(
            organization_id=org_id,
            user_id=member_data.user_id,
            role=member_data.role,
            added_by_user_id=current_user_id,
        )
        return OrganizationMemberResponse.model_validate(member)
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete(
    "/{org_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove organization member",
    description="Remove a member from organization (requires owner or admin role)",
)
async def remove_member(
    org_id: UUID,
    user_id: str,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> None:
    """
    Remove member from organization.

    Only owners and admins can remove members.

    Args:
        org_id: Organization UUID
        user_id: User ID to remove
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user lacks permission
        HTTPException 404: If organization not found
    """
    org_service = OrganizationService(db)

    try:
        await org_service.remove_member(
            organization_id=org_id,
            user_id=user_id,
            removed_by_user_id=current_user_id,
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post(
    "/{org_id}/recover",
    response_model=OrganizationResponse,
    summary="Recover soft-deleted organization",
    description="Recover organization within 30-day recovery window (requires owner role)",
)
async def recover_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> OrganizationResponse:
    """
    Recover soft-deleted organization.

    Task: T202 [US8] - POST /organizations/{org_id}/recover

    Only owners can recover organizations.
    Organization must have been soft-deleted (deleted_at not NULL).

    Args:
        org_id: Organization UUID
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        OrganizationResponse with recovered organization details

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not owner or org not deleted
        HTTPException 404: If organization not found
    """
    org_service = OrganizationService(db)

    try:
        org = await org_service.recover_organization(
            organization_id=org_id,
            recovered_by_user_id=current_user_id,
        )
        return OrganizationResponse.model_validate(org)
    except OrganizationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )
    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
