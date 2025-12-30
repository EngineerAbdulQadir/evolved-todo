"""
Application settings module.

Loads configuration from environment variables and .env file.
"""

from pathlib import Path
from pydantic_settings import BaseSettings

# Get the backend directory (two levels up from this file)
BACKEND_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application settings
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"
    debug: bool = True

    # Database settings
    database_url: str = "postgresql+asyncpg://user:password@localhost/evolved_todo"

    # Authentication settings
    better_auth_secret: str = "your-secret-key-here"

    # Phase 3: AI Agent settings
    openai_api_key: str = ""

    # MCP Standalone Server settings (optional - used when running standalone MCP server)
    mcp_transport: str = "http"
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8001
    mcp_api_keys: str = ""
    log_level: str = "INFO"

    class Config:
        """Pydantic settings configuration."""

        env_file = str(BACKEND_DIR / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False


import logging

# Set up logger for settings module
logger = logging.getLogger(__name__)

# Global settings instance
settings = Settings()

# Debug output (remove in production)
logger.debug(f"[DEBUG] Loaded .env from: {BACKEND_DIR / '.env'}")
logger.debug(f"[DEBUG] DATABASE_URL: {settings.database_url[:60]}...")
logger.debug(f"[DEBUG] FRONTEND_URL: {settings.frontend_url}")
