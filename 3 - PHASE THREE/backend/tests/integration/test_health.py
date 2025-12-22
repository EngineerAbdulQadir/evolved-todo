"""
Integration tests for health check endpoint (T228).
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_health_check_success(test_client: AsyncClient):
    response = await test_client.get("/api/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["api"] == "ok"
    assert data["database"] == "ok"
    assert "error" not in data


@pytest.mark.asyncio
async def test_health_check_database_error(test_client: AsyncClient):
    """Test health check returns error when database connection fails."""
    # Patch the database session to raise an exception
    with patch('app.api.health.get_session') as mock_get_session:
        # Create a mock session that raises an exception on execute
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Database connection failed")

        # Make get_session return our mock session
        async def mock_dependency():
            yield mock_session

        mock_get_session.return_value = mock_dependency()

        # Override the dependency in the app
        from app.main import app
        from app.core.database import get_session

        app.dependency_overrides[get_session] = mock_dependency

        try:
            response = await test_client.get("/api/health")

            # Health endpoint should still return 200 but with error status
            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "unhealthy"
            assert data["api"] == "ok"
            assert data["database"] == "error"
            assert "error" in data
            assert "Database connection failed" in data["error"]
        finally:
            # Clean up dependency override
            app.dependency_overrides = {}
