import os
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from fastapi import FastAPI, HTTPException
import requests
import json

class BaseMCPServer(ABC):
    """Base class for all MCP (Multi-Channel Provider) servers"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize MCP server with configuration"""
        self.config = config
        self.app = FastAPI(
            title=f"{self.get_name()} MCP Server",
            description=f"MCP Server for {self.get_name()}",
            version="1.0.0"
        )
        self.setup_routes()
        self.setup_health_check()

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of this MCP server"""
        pass

    @abstractmethod
    def get_source_type(self) -> str:
        """Get the source type (e.g., 'jira', 'slack')"""
        pass

    def setup_routes(self):
        """Setup common routes for all MCP servers"""
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "server": self.get_name()}

    def setup_health_check(self):
        """Setup health check endpoint"""
        pass

    @abstractmethod
    async def fetch_data(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch data from the external source"""
        pass

    @abstractmethod
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for items in the external source"""
        pass

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the MCP server"""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)

class JiraMCPServer(BaseMCPServer):
    """MCP Server for Jira (read-only)"""

    def get_name(self) -> str:
        return "Jira"

    def get_source_type(self) -> str:
        return "jira"

    async def fetch_data(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch issues from Jira"""
        # In a real implementation, this would call Jira API
        # For now, return mock data
        return [
            {
                "id": "JIRA-1",
                "key": "PROJ-1",
                "summary": "Implement MCP Server Framework",
                "description": "Create base MCP server template",
                "status": "In Progress",
                "assignee": "developer@example.com"
            }
        ]

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search Jira issues"""
        # Mock implementation
        return [
            {
                "id": "JIRA-1",
                "key": "PROJ-1",
                "summary": f"Search results for: {query}",
                "description": "Mock search result",
                "status": "Open",
                "assignee": "developer@example.com"
            }
        ]

class SlackMCPServer(BaseMCPServer):
    """MCP Server for Slack (read-only)"""

    def get_name(self) -> str:
        return "Slack"

    def get_source_type(self) -> str:
        return "slack"

    async def fetch_data(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch messages from Slack"""
        # Mock implementation
        return [
            {
                "id": "SLACK-1",
                "channel": "general",
                "text": "Hello world!",
                "timestamp": "2023-01-01T00:00:00Z",
                "user": "user1"
            }
        ]

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search Slack messages"""
        # Mock implementation
        return [
            {
                "id": "SLACK-1",
                "channel": "general",
                "text": f"Search result for: {query}",
                "timestamp": "2023-01-01T00:00:00Z",
                "user": "user1"
            }
        ]

# Test the MCP servers
if __name__ == "__main__":
    # Test Jira MCP Server
    jira_config = {
        "api_url": "https://example.atlassian.net",
        "username": "user@example.com",
        "api_token": "mock_token"
    }
    jira_server = JiraMCPServer(jira_config)

    # Test Slack MCP Server
    slack_config = {
        "api_url": "https://slack.com/api",
        "token": "mock_token"
    }
    slack_server = SlackMCPServer(slack_config)

    print("MCP Servers initialized successfully!")
    print(f"Jira Server: {jira_server.get_name()}")
    print(f"Slack Server: {slack_server.get_name()}")
