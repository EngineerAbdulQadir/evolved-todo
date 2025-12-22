import pytest
from pydantic import ValidationError
from app.mcp.schemas import MCPToolInput, MCPToolOutput, MCPErrorOutput, MCPErrorCode


def test_mcp_tool_input_valid():
    """Test valid MCP tool input."""
    data = {"user_id": "test_user_123"}
    input_obj = MCPToolInput(**data)
    
    assert input_obj.user_id == "test_user_123"


def test_mcp_tool_input_missing_user_id():
    """Test MCP tool input validation with missing user_id."""
    with pytest.raises(ValidationError):
        MCPToolInput()


def test_mcp_tool_output_valid():
    """Test valid MCP tool output."""
    data = {"status": "success", "message": "Operation completed"}
    output_obj = MCPToolOutput(**data)
    
    assert output_obj.status == "success"
    assert output_obj.message == "Operation completed"


def test_mcp_error_output_valid():
    """Test valid MCP error output."""
    data = {
        "error_code": MCPErrorCode.INVALID_INPUT,
        "details": {"field": "value"}
    }
    error_obj = MCPErrorOutput(**data)
    
    assert error_obj.status == "error"
    assert error_obj.error_code == MCPErrorCode.INVALID_INPUT
    assert error_obj.details == {"field": "value"}


def test_mcp_error_codes():
    """Test that all expected error codes exist."""
    assert hasattr(MCPErrorCode, 'TASK_NOT_FOUND')
    assert hasattr(MCPErrorCode, 'INVALID_INPUT')
    assert hasattr(MCPErrorCode, 'UNAUTHORIZED')
    assert hasattr(MCPErrorCode, 'PERMISSION_DENIED')
    assert hasattr(MCPErrorCode, 'DATABASE_ERROR')
    assert hasattr(MCPErrorCode, 'UNKNOWN_ERROR')
    
    assert MCPErrorCode.TASK_NOT_FOUND == "TASK_NOT_FOUND"
    assert MCPErrorCode.INVALID_INPUT == "INVALID_INPUT"
    assert MCPErrorCode.UNAUTHORIZED == "UNAUTHORIZED"
    assert MCPErrorCode.PERMISSION_DENIED == "PERMISSION_DENIED"
    assert MCPErrorCode.DATABASE_ERROR == "DATABASE_ERROR"
    assert MCPErrorCode.UNKNOWN_ERROR == "UNKNOWN_ERROR"