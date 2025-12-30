"""
Health check endpoint for Kubernetes deployment (Phase 4 - T008).

This module provides a comprehensive health check endpoint that can be used by:
- Kubernetes liveness/readiness/startup probes (ADR-001)
- Load balancers
- Container orchestration platforms
- Monitoring tools
- Deployment automation

Returns:
    - HTTP 200: Service is healthy
    - HTTP 503: Service is unhealthy (database connection failed)
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

from app.core.database import get_session

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Health check endpoint for Kubernetes probes",
    description="Check if the API and database are healthy. Returns 200 for healthy, 503 for unhealthy.",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2025-12-25T20:05:00Z",
                        "api": "ok",
                        "database": "ok"
                    }
                }
            }
        },
        503: {
            "description": "Service is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "timestamp": "2025-12-25T20:05:00Z",
                        "api": "ok",
                        "database": "error",
                        "error": "Connection refused"
                    }
                }
            }
        }
    }
)
async def health_check(response: Response, db: AsyncSession = Depends(get_session)):
    """
    Perform health check on API and database.

    Phase 4 requirements (T008):
    - Returns JSON with status, timestamp, database connection status
    - Returns HTTP 200 when healthy
    - Returns HTTP 503 when unhealthy (for Kubernetes liveness probe failures)

    Args:
        response: FastAPI Response object for status code modification
        db: Database session dependency

    Returns:
        dict: Health status with timestamp, API status, database status
    """
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    try:
        # Test database connection with timeout
        await db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "timestamp": timestamp,
            "api": "ok",
            "database": "ok",
        }
    except Exception as e:
        # Return 503 Service Unavailable for unhealthy state
        response.status_code = 503
        return {
            "status": "unhealthy",
            "timestamp": timestamp,
            "api": "ok",
            "database": "error",
            "error": str(e),
        }
