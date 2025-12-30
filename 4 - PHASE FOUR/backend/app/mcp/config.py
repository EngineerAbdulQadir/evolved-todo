"""
MCP Standalone Server Configuration

Configuration for running the MCP server as a standalone service
with support for both stdio and HTTP transports.

Uses the main application settings from app.core.settings.
"""

from app.core.settings import settings


class MCPServerConfig:
    """
    Configuration wrapper for standalone MCP server.

    Uses the main application settings to avoid duplication.
    """

    def __init__(self):
        self._settings = settings

    @property
    def mcp_transport(self) -> str:
        """Transport mode (stdio or http)."""
        return self._settings.mcp_transport

    @property
    def mcp_host(self) -> str:
        """HTTP server host."""
        return self._settings.mcp_host

    @property
    def mcp_port(self) -> int:
        """HTTP server port."""
        return self._settings.mcp_port

    @property
    def mcp_api_keys(self) -> str:
        """Comma-separated API keys."""
        return self._settings.mcp_api_keys

    @property
    def database_url(self) -> str:
        """Database connection URL."""
        return self._settings.database_url

    @property
    def log_level(self) -> str:
        """Logging level."""
        return self._settings.log_level

    @property
    def api_keys_list(self) -> list[str]:
        """Parse comma-separated API keys into list."""
        if not self.mcp_api_keys:
            return []
        return [key.strip() for key in self.mcp_api_keys.split(",") if key.strip()]

    @property
    def is_stdio_transport(self) -> bool:
        """Check if using stdio transport."""
        return self.mcp_transport.lower() == "stdio"

    @property
    def is_http_transport(self) -> bool:
        """Check if using HTTP transport."""
        return self.mcp_transport.lower() == "http"


def get_config() -> MCPServerConfig:
    """Get MCP server configuration."""
    return MCPServerConfig()
