"""
Unit tests for the database connection and session management.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.database import close_db, DATABASE_URL
from app.core.settings import settings


def test_database_url_from_settings():
    """Tests that the DATABASE_URL is read correctly from settings."""
    assert DATABASE_URL == settings.database_url


@pytest.mark.asyncio
async def test_close_db():
    """Tests that close_db disposes the engine."""
    from unittest.mock import AsyncMock
    from app.core import database

    # Temporarily replace the real engine with a mock
    original_engine = database.engine
    mock_engine = AsyncMock()
    database.engine = mock_engine

    await close_db()

    mock_engine.dispose.assert_called_once()

    # Restore the original engine
    database.engine = original_engine