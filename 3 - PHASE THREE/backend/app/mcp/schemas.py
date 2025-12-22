"""MCP tool base schema types.

This module defines Pydantic base classes for all MCP tool inputs and outputs,
ensuring type safety and validation.

Task: T012 - Create MCP tool base schema types
Spec: specs/003-phase3-ai-chatbot/contracts/mcp-tools.md
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MCPToolInput(BaseModel):
    """Base class for all MCP tool inputs."""

    user_id: str = Field(..., description="User ID from JWT token for data isolation")

    class Config:
        """Pydantic configuration."""

        # Use discriminator for tool type identification
        extra = "forbid"  # Reject unknown fields
        use_enum_values = True
        json_schema_extra = {"additionalProperties": False}


class MCPToolOutput(BaseModel):
    """Base class for all MCP tool outputs."""

    status: str = Field(..., description="Operation status: 'success' or 'error'")
    message: Optional[str] = Field(None, description="Human-readable message")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_schema_extra = {"additionalProperties": False}


class MCPErrorOutput(MCPToolOutput):
    """Standard error response for MCP tools."""

    status: str = Field(default="error", description="Always 'error'")
    error_code: str = Field(..., description="Machine-readable error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Task not found",
                "error_code": "TASK_NOT_FOUND",
                "details": {"task_id": 999},
            }
        }


# Standard error codes
class MCPErrorCode:
    """Standard error codes for MCP tools."""

    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    INVALID_INPUT = "INVALID_INPUT"
    UNAUTHORIZED = "UNAUTHORIZED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    DATABASE_ERROR = "DATABASE_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
