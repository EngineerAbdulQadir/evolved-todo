"""
Audit Service - Business Logic Layer

Provides audit log creation and querying with JSONB metadata support.

References:
- ADR-003: Soft Delete and Audit Trail Strategy
- Constitution v5.0.0 Principle XXII: Audit Trails & Change History
- specs/005-multi-tenant-collab/plan.md § Component Breakdown
"""

from typing import Optional
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.audit_log import AuditLog


async def log_action(
    session: AsyncSession,
    organization_id: UUID,
    resource_type: str,
    resource_id: UUID,
    action: str,
    user_id: Optional[UUID] = None,
    context: Optional[dict] = None,
) -> AuditLog:
    """
    Create an audit log entry for a CRUD operation.

    Tracks WHO (user_id), WHAT (resource_type, resource_id, action),
    WHEN (created_at), and context for compliance and debugging.

    Args:
        session: Database session
        organization_id: Organization UUID (tenant context)
        resource_type: Type of resource (e.g., "organization", "team", "project", "task")
        resource_id: UUID of the resource being acted upon
        action: Action performed (e.g., "create", "update", "delete", "add_member")
        user_id: UUID of user performing the action (NULL for system events)
        context: JSONB context with before/after values, details (default: empty dict)

    Returns:
        Created AuditLog instance

    Examples:
        # Create organization
        await log_action(
            session=session,
            organization_id=org_id,
            user_id=user_id,
            resource_type="organization",
            resource_id=org_id,
            action="create",
            context={"name": "Acme Corp", "slug": "acme-corp"}
        )

        # Update task status
        await log_action(
            session=session,
            organization_id=org_id,
            user_id=user_id,
            resource_type="task",
            resource_id=task_id,
            action="update",
            context={
                "changes": {
                    "status": {"before": "pending", "after": "completed"}
                }
            }
        )

        # Soft delete organization
        await log_action(
            session=session,
            organization_id=org_id,
            user_id=user_id,
            resource_type="organization",
            resource_id=org_id,
            action="soft_delete",
            context={
                "recovery_until": "2025-01-28T00:00:00Z",
                "cascade_affected": {
                    "teams": 5,
                    "projects": 12,
                    "tasks": 143
                }
            }
        )

    Task: T172 [US5] - Implement log_action()
    ADR-003: Soft Delete and Audit Trail Strategy
    """
    # Create audit log entry
    audit_log = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        context=context or {},
    )

    # Add to session and flush to get ID
    session.add(audit_log)
    await session.flush()

    return audit_log


async def query_audit_logs(
    session: AsyncSession,
    organization_id: UUID,
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    action: Optional[str] = None,
    user_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
) -> list[AuditLog]:
    """
    Query audit logs with filters.

    Performance requirement: <200ms for 30-day history queries.

    Args:
        session: Database session
        organization_id: Organization UUID (required for tenant isolation)
        resource_type: Filter by resource type (e.g., "task", "project")
        resource_id: Filter by specific resource UUID
        action: Filter by action (e.g., "create", "update", "delete")
        user_id: Filter by user who performed the action
        start_date: Filter by date range start (ISO format)
        end_date: Filter by date range end (ISO format)
        limit: Maximum number of results (default: 100, max: 1000)

    Returns:
        List of AuditLog entries matching filters, ordered by created_at DESC

    Task: T173 [US5] - Implement query_audit_logs()
    ADR-003: Soft Delete and Audit Trail Strategy
    """
    from sqlmodel import select
    from datetime import datetime

    # Build query with organization filter (multi-tenant isolation)
    query = select(AuditLog).where(AuditLog.organization_id == organization_id)

    # Apply optional filters
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    if resource_id:
        query = query.where(AuditLog.resource_id == resource_id)

    if action:
        query = query.where(AuditLog.action == action)

    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.where(AuditLog.created_at >= start_dt)

    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.where(AuditLog.created_at <= end_dt)

    # Order by most recent first
    query = query.order_by(AuditLog.created_at.desc())

    # Apply limit (cap at 1000 for performance)
    limit = min(limit, 1000)
    query = query.limit(limit)

    # Execute query
    result = await session.execute(query)
    logs = result.scalars().all()

    return list(logs)


async def cleanup_old_audit_logs(
    session: AsyncSession,
    retention_days: int = 180,
) -> int:
    """
    Background job to delete audit logs older than retention period.

    Default retention: 180 days (configurable).

    Args:
        session: Database session
        retention_days: Number of days to retain audit logs (default: 180)

    Returns:
        Number of audit log entries deleted

    Task: Background job for audit log retention
    ADR-003: Soft Delete and Audit Trail Strategy
    """
    from sqlmodel import select, delete
    from datetime import datetime, timedelta

    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

    # Delete old audit logs
    delete_query = delete(AuditLog).where(AuditLog.created_at < cutoff_date)

    result = await session.execute(delete_query)
    await session.commit()

    return result.rowcount
