import pytest
from backend.mcp_servers.base_mcp_server import JiraMCPServer, SlackMCPServer

def test_jira_mcp_server():
    """Test Jira MCP Server"""
    config = {
        "api_url": "https://example.atlassian.net",
        "username": "user@example.com",
        "api_token": "mock_token"
    }
    server = JiraMCPServer(config)

    assert server.get_name() == "Jira"
    assert server.get_source_type() == "jira"

    # Test fetch_data
    data = server.fetch_data()
    assert len(data) > 0
    assert "id" in data[0]
    assert "key" in data[0]

    # Test search
    results = server.search("test query")
    assert len(results) > 0
    assert "summary" in results[0]

def test_slack_mcp_server():
    """Test Slack MCP Server"""
    config = {
        "api_url": "https://slack.com/api",
        "token": "mock_token"
    }
    server = SlackMCPServer(config)

    assert server.get_name() == "Slack"
    assert server.get_source_type() == "slack"

    # Test fetch_data
    data = server.fetch_data()
    assert len(data) > 0
    assert "id" in data[0]
    assert "channel" in data[0]

    # Test search
    results = server.search("test query")
    assert len(results) > 0
    assert "text" in results[0]

def test_mcp_server_routes():
    """Test MCP Server routes"""
    from fastapi.testclient import TestClient

    config = {
        "api_url": "https://example.atlassian.net",
        "username": "user@example.com",
        "api_token": "mock_token"
    }
    server = JiraMCPServer(config)
    client = TestClient(server.app)

    # Test health check
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["server"] == "Jira"
