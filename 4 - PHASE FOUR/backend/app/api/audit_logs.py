"""
Audit Log API Routes

RESTful endpoints for querying audit trails with organization scoping.

References:
- specs/005-multi-tenant-collab/contracts/audit-logs.yaml
- ADR-003: Soft Delete and Audit Trail Strategy
- Constitution v5.0.0 Principle XXII: Audit Trails & Change History
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.middleware.auth import get_current_user_id
from app.models import PermissionDeniedError
from app.models.audit_log import AuditLog, AuditLogRead
from app.services import audit_service
from app.services.organization_service import OrganizationService


router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get(
    "",
    response_model=List[AuditLogRead],
    summary="Query audit logs",
    description="Query audit logs with filters (requires organization membership)",
)
async def query_audit_logs(
    organization_id: UUID = Query(..., description="Organization UUID"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[UUID] = Query(None, description="Filter by resource UUID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    user_id: Optional[UUID] = Query(None, description="Filter by user UUID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> List[AuditLogRead]:
    """
    Query audit logs with optional filters.

    Performance target: <200ms for 30-day history.

    Args:
        organization_id: Organization UUID (required for tenant isolation)
        resource_type: Filter by resource type (e.g., "task", "project")
        resource_id: Filter by specific resource UUID
        action: Filter by action (e.g., "create", "update", "delete")
        user_id: Filter by user who performed the action
        start_date: Filter by date range start (ISO format)
        end_date: Filter by date range end (ISO format)
        limit: Maximum number of results (default: 100, max: 1000)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        List of audit log entries matching filters

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not organization member

    Task: T175 [US5] - GET /audit-logs
    """
    # Verify user is organization member
    org_service = OrganizationService(db)
    try:
        await org_service.get_organization(
            organization_id=organization_id,
            user_id=current_user_id,
        )
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Not an organization member",
        )

    # Query audit logs
    logs = await audit_service.query_audit_logs(
        session=db,
        organization_id=organization_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    return [AuditLogRead.model_validate(log) for log in logs]


@router.get(
    "/organization/{org_id}",
    response_model=List[AuditLogRead],
    summary="Get organization audit logs",
    description="Get all audit logs for organization (requires organization membership)",
)
async def get_organization_audit_logs(
    org_id: UUID,
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> List[AuditLogRead]:
    """
    Get all audit logs for an organization.

    Args:
        org_id: Organization UUID
        start_date: Filter by date range start (ISO format)
        end_date: Filter by date range end (ISO format)
        limit: Maximum number of results (default: 100, max: 1000)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        List of all audit log entries for the organization

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not organization member

    Task: T176 [US5] - GET /audit-logs/organization/{org_id}
    """
    # Verify user is organization member
    org_service = OrganizationService(db)
    try:
        await org_service.get_organization(
            organization_id=org_id,
            user_id=current_user_id,
        )
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Not an organization member",
        )

    # Query all audit logs for organization
    logs = await audit_service.query_audit_logs(
        session=db,
        organization_id=org_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    return [AuditLogRead.model_validate(log) for log in logs]


@router.get(
    "/resource/{resource_type}/{resource_id}",
    response_model=List[AuditLogRead],
    summary="Get resource audit logs",
    description="Get audit logs for specific resource (requires organization membership)",
)
async def get_resource_audit_logs(
    resource_type: str,
    resource_id: UUID,
    organization_id: UUID = Query(..., description="Organization UUID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    db: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> List[AuditLogRead]:
    """
    Get audit logs for a specific resource.

    Args:
        resource_type: Type of resource (e.g., "task", "project", "team")
        resource_id: Resource UUID
        organization_id: Organization UUID (for verification)
        limit: Maximum number of results (default: 100, max: 1000)
        db: Database session
        current_user_id: Authenticated user ID from JWT token

    Returns:
        List of audit log entries for the resource

    Raises:
        HTTPException 401: If unauthenticated
        HTTPException 403: If user is not organization member

    Task: T177 [US5] - GET /audit-logs/resource/{resource_type}/{resource_id}
    """
    # Verify user is organization member
    org_service = OrganizationService(db)
    try:
        await org_service.get_organization(
            organization_id=organization_id,
            user_id=current_user_id,
        )
    except PermissionDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Not an organization member",
        )

    # Query audit logs for specific resource
    logs = await audit_service.query_audit_logs(
        session=db,
        organization_id=organization_id,
        resource_type=resource_type,
        resource_id=resource_id,
        limit=limit,
    )

    return [AuditLogRead.model_validate(log) for log in logs]
