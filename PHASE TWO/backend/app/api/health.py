"""
Health check endpoint for monitoring and deployment (T228).

This module provides a simple health check endpoint that can be used by:
- Load balancers
- Container orchestration platforms (Kubernetes, etc.)
- Monitoring tools
- Deployment automation
"""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

from app.core.database import get_session

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Health check",
    description="Check if the API and database are healthy",
    status_code=200,
)
async def health_check(db: AsyncSession = Depends(get_session)):
    """
    Perform health check on API and database.

    Returns:
        dict: Status information including API and database health

    Raises:
        HTTPException 503: If database connection fails
    """
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "api": "ok",
            "database": "ok",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "api": "ok",
            "database": "error",
            "error": str(e),
        }
