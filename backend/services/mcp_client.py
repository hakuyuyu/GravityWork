"""
MCP Client Service

Provides a unified interface for calling MCP servers (Jira, Slack, GitHub)
from the LangGraph agent.
"""
import os
import httpx
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MCPToolResult(BaseModel):
    """Result from an MCP tool call."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MCPClient:
    """
    Client for interacting with MCP servers.
    """
    
    def __init__(self):
        self.jira_url = os.getenv("JIRA_MCP_URL", "http://localhost:8001")
        self.slack_url = os.getenv("SLACK_MCP_URL", "http://localhost:8002")
        self.github_url = os.getenv("GITHUB_MCP_URL", "http://localhost:8003")
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def call_jira(self, action: str, params: Dict[str, Any]) -> MCPToolResult:
        """Call Jira MCP server."""
        try:
            # For now, use local mock implementation
            from mcp_servers.mcp_server_jira import JiraMCPServer
            server = JiraMCPServer()
            result = server.fetch_data({"action": action, **params})
            return MCPToolResult(success=True, data=result)
        except Exception as e:
            logger.error(f"Jira MCP call failed: {e}")
            return MCPToolResult(success=False, error=str(e))
    
    async def call_slack(self, action: str, params: Dict[str, Any]) -> MCPToolResult:
        """Call Slack MCP server."""
        try:
            from mcp_servers.mcp_server_slack import SlackMCPServer
            server = SlackMCPServer()
            result = server.fetch_data({"action": action, **params})
            return MCPToolResult(success=True, data=result)
        except Exception as e:
            logger.error(f"Slack MCP call failed: {e}")
            return MCPToolResult(success=False, error=str(e))
    
    async def get_ticket_status(self, ticket_id: str) -> MCPToolResult:
        """Get status of a Jira ticket."""
        return await self.call_jira("get_ticket", {"ticket_id": ticket_id})
    
    async def search_tickets(self, query: str, project: Optional[str] = None) -> MCPToolResult:
        """Search Jira tickets."""
        params = {"query": query}
        if project:
            params["project"] = project
        return await self.call_jira("search", params)
    
    async def create_ticket(self, summary: str, description: str, project: str) -> MCPToolResult:
        """Create a new Jira ticket."""
        return await self.call_jira("create", {
            "summary": summary,
            "description": description,
            "project": project
        })
    
    async def get_slack_messages(self, channel: str, limit: int = 10) -> MCPToolResult:
        """Get recent Slack messages from a channel."""
        return await self.call_slack("get_messages", {
            "channel": channel,
            "limit": limit
        })
    
    async def send_slack_message(self, channel: str, message: str) -> MCPToolResult:
        """Send a message to Slack."""
        return await self.call_slack("send_message", {
            "channel": channel,
            "message": message
        })
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

# Singleton instance
_mcp_client = None

def get_mcp_client() -> MCPClient:
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
