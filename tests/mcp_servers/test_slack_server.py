"""
Tests for Slack MCP Server
"""

import pytest
from fastapi.testclient import TestClient
from mcp_servers.mcp_server_slack import SlackMCPServer, create_slack_server
from unittest.mock import patch, MagicMock
import os
from datetime import datetime

@pytest.fixture
def slack_server():
    """Create a Slack server for testing"""
    config = MagicMock()
    config.server_name = "Slack"
    config.api_base_url = "http://slack-api.com"
    config.api_key = "test-key"
    config.timeout = 30
    config.max_retries = 3

    server = SlackMCPServer(config)
    return server

def test_slack_health_check(slack_server):
    """Test Slack health check endpoint"""
    client = TestClient(slack_server.get_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["server"] == "Slack"

@patch.object(SlackMCPServer, '_make_request')
def test_get_messages(mock_make_request, slack_server):
    """Test getting Slack messages"""
    mock_make_request.return_value = {
        "messages": [
            {
                "ts": "1672531200.000000",
                "text": "Hello world",
                "user": "U123456",
                "thread_ts": None,
                "reactions": []
            },
            {
                "ts": "1672531201.000000",
                "text": "How are you?",
                "user": "U789012",
                "thread_ts": None,
                "reactions": [{"name": "thumbsup", "count": 1}]
            }
        ],
        "has_more": False
    }

    client = TestClient(slack_server.get_app())
    response = client.get("/messages/C123456")
    assert response.status_code == 200
    data = response.json()
    assert data["channel"] == "C123456"
    assert len(data["messages"]) == 2
    assert data["messages"][0]["text"] == "Hello world"

@patch.object(SlackMCPServer, '_make_request')
def test_get_channels(mock_make_request, slack_server):
    """Test getting Slack channels"""
    mock_make_request.return_value = {
        "channels": [
            {
                "id": "C123456",
                "name": "general",
                "is_channel": True,
                "is_group": False,
                "is_im": False,
                "created": 1672531200,
                "creator": "U123456"
            },
            {
                "id": "C789012",
                "name": "random",
                "is_channel": True,
                "is_group": False,
                "is_im": False,
                "created": 1672531201,
                "creator": "U789012"
            }
        ]
    }

    client = TestClient(slack_server.get_app())
    response = client.get("/channels")
    assert response.status_code == 200
    data = response.json()
    assert len(data["channels"]) == 2
    assert data["channels"][0]["name"] == "general"

@patch.object(SlackMCPServer, '_make_request')
def test_get_users(mock_make_request, slack_server):
    """Test getting Slack users"""
    mock_make_request.return_value = {
        "members": [
            {
                "id": "U123456",
                "name": "john.doe",
                "real_name": "John Doe",
                "deleted": False,
                "is_bot": False,
                "profile": {
                    "email": "john@example.com"
                }
            },
            {
                "id": "U789012",
                "name": "jane.smith",
                "real_name": "Jane Smith",
                "deleted": False,
                "is_bot": False,
                "profile": {
                    "email": "jane@example.com"
                }
            }
        ]
    }

    client = TestClient(slack_server.get_app())
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data["users"]) == 2
    assert data["users"][0]["name"] == "john.doe"
    assert data["users"][0]["email"] == "john@example.com"

@patch.object(SlackMCPServer, '_make_request')
def test_get_channel_info(mock_make_request, slack_server):
    """Test getting Slack channel info"""
    mock_make_request.return_value = {
        "channel": {
            "id": "C123456",
            "name": "general",
            "is_channel": True,
            "is_group": False,
            "is_im": False,
            "created": 1672531200,
            "creator": "U123456"
        }
    }

    client = TestClient(slack_server.get_app())
    response = client.get("/channels/C123456/info")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "C123456"
    assert data["name"] == "general"

def test_create_slack_server():
    """Test Slack server factory function"""
    with patch.dict(os.environ, {
        "SLACK_API_BASE_URL": "http://test-slack.com",
        "SLACK_API_KEY": "test-key"
    }):
        server = create_slack_server()
        assert server.config.server_name == "Slack"
        assert server.config.api_base_url == "http://test-slack.com"
        assert server.config.api_key == "test-key"
