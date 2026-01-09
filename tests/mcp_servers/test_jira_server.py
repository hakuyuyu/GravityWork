"""
Tests for Jira MCP Server
"""

import pytest
from fastapi.testclient import TestClient
from mcp_servers.mcp_server_jira import JiraMCPServer, create_jira_server, JiraIssue
from unittest.mock import patch, MagicMock
import os

@pytest.fixture
def jira_server():
    """Create a Jira server for testing"""
    config = MagicMock()
    config.server_name = "Jira"
    config.api_base_url = "http://jira-api.com"
    config.api_key = "test-key"
    config.timeout = 30
    config.max_retries = 3

    server = JiraMCPServer(config)
    return server

def test_jira_health_check(jira_server):
    """Test Jira health check endpoint"""
    client = TestClient(jira_server.get_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["server"] == "Jira"

@patch.object(JiraMCPServer, '_make_request')
def test_get_issue(mock_make_request, jira_server):
    """Test getting a Jira issue"""
    mock_make_request.return_value = {
        "id": "12345",
        "key": "PROJ-123",
        "fields": {
            "summary": "Test Issue",
            "description": "Test description",
            "status": {"name": "In Progress"},
            "issuetype": {"name": "Task"},
            "created": "2023-01-01T00:00:00.000+0000",
            "updated": "2023-01-02T00:00:00.000+0000",
            "priority": {"name": "Medium"},
            "assignee": {"displayName": "John Doe"},
            "reporter": {"displayName": "Jane Smith"}
        }
    }

    client = TestClient(jira_server.get_app())
    response = client.get("/issues/PROJ-123")
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "PROJ-123"
    assert data["summary"] == "Test Issue"
    assert data["status"] == "In Progress"

@patch.object(JiraMCPServer, '_make_request')
def test_get_project(mock_make_request, jira_server):
    """Test getting a Jira project"""
    mock_make_request.return_value = {
        "id": "10000",
        "key": "PROJ",
        "name": "Test Project",
        "description": "Test project description"
    }

    client = TestClient(jira_server.get_app())
    response = client.get("/projects/PROJ")
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "PROJ"
    assert data["name"] == "Test Project"

@patch.object(JiraMCPServer, '_make_request')
def test_search_issues(mock_make_request, jira_server):
    """Test searching Jira issues"""
    mock_make_request.return_value = {
        "total": 2,
        "issues": [
            {
                "id": "12345",
                "key": "PROJ-123",
                "fields": {
                    "summary": "Test Issue 1",
                    "description": "Description 1",
                    "status": {"name": "In Progress"},
                    "issuetype": {"name": "Task"},
                    "created": "2023-01-01T00:00:00.000+0000",
                    "updated": "2023-01-02T00:00:00.000+0000",
                    "priority": {"name": "Medium"},
                    "assignee": {"displayName": "John Doe"},
                    "reporter": {"displayName": "Jane Smith"}
                }
            },
            {
                "id": "12346",
                "key": "PROJ-124",
                "fields": {
                    "summary": "Test Issue 2",
                    "description": "Description 2",
                    "status": {"name": "Done"},
                    "issuetype": {"name": "Bug"},
                    "created": "2023-01-03T00:00:00.000+0000",
                    "updated": "2023-01-04T00:00:00.000+0000",
                    "priority": {"name": "High"},
                    "assignee": None,
                    "reporter": {"displayName": "Jane Smith"}
                }
            }
        ]
    }

    client = TestClient(jira_server.get_app())
    response = client.get("/issues?project_key=PROJ&status=In Progress")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["issues"]) == 2
    assert data["issues"][0]["key"] == "PROJ-123"

def test_create_jira_server():
    """Test Jira server factory function"""
    with patch.dict(os.environ, {
        "JIRA_API_BASE_URL": "http://test-jira.com",
        "JIRA_API_KEY": "test-key"
    }):
        server = create_jira_server()
        assert server.config.server_name == "Jira"
        assert server.config.api_base_url == "http://test-jira.com"
        assert server.config.api_key == "test-key"
