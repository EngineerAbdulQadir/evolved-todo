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

    class Config:
        """Pydantic settings configuration."""

        env_file = str(BACKEND_DIR / ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Debug output (remove in production)
print(f"[DEBUG] Loaded .env from: {BACKEND_DIR / '.env'}")
print(f"[DEBUG] DATABASE_URL: {settings.database_url[:60]}...")
print(f"[DEBUG] FRONTEND_URL: {settings.frontend_url}")
