"""
Tests for Base MCP Server
"""

import pytest
from fastapi.testclient import TestClient
from mcp_servers.base_mcp_server import MCPServer, MCPConfig
from unittest.mock import patch, MagicMock
import os

@pytest.fixture
def base_server():
    """Create a base MCP server for testing"""
    config = MCPConfig(
        server_name="TestServer",
        api_base_url="http://test-api.com",
        api_key="test-key"
    )
    return MCPServer(config)

def test_health_check(base_server):
    """Test health check endpoint"""
    client = TestClient(base_server.get_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["server"] == "TestServer"

def test_root_endpoint(base_server):
    """Test root endpoint"""
    client = TestClient(base_server.get_app())
    response = client.get("/")
    assert response.status_code == 200
    assert "TestServer MCP Server" in response.json()["message"]

@patch('requests.request')
def test_make_request_success(mock_request, base_server):
    """Test successful API request"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"test": "data"}
    mock_request.return_value = mock_response

    result = base_server._make_request("GET", "test/endpoint")
    assert result == {"test": "data"}
    mock_request.assert_called_once()

@patch('requests.request')
def test_make_request_retry_and_fail(mock_request, base_server):
    """Test request retry and failure"""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        base_server._make_request("GET", "test/endpoint")

    assert "External API error" in str(exc_info.value)
    assert mock_request.call_count == 3  # Should retry 3 times

@patch('requests.request')
def test_make_request_unauthorized(mock_request, base_server):
    """Test unauthorized request"""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        base_server._make_request("GET", "test/endpoint")

    assert "Unauthorized access" in str(exc_info.value)

def test_make_request_no_base_url(base_server):
    """Test request without base URL"""
    base_server.config.api_base_url = None

    with pytest.raises(Exception) as exc_info:
        base_server._make_request("GET", "test/endpoint")

    assert "API base URL not configured" in str(exc_info.value)
