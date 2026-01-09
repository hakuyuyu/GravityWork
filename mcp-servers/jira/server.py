"""
MCP Server for Jira - GravityWork
Provides real-time access to Jira tickets, sprints, and velocity data.
"""

import os
from typing import Any, Optional
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP server
server = Server("mcp-server-jira")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Jira tools."""
    return [
        Tool(
            name="get_ticket",
            description="Get details of a Jira ticket by key (e.g., PROJ-123)",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_key": {
                        "type": "string",
                        "description": "The Jira ticket key (e.g., PROJ-123)"
                    }
                },
                "required": ["ticket_key"]
            }
        ),
        Tool(
            name="search_tickets",
            description="Search for Jira tickets using JQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "jql": {
                        "type": "string",
                        "description": "JQL query string"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["jql"]
            }
        ),
        Tool(
            name="get_sprint_velocity",
            description="Get velocity metrics for a sprint",
            inputSchema={
                "type": "object",
                "properties": {
                    "board_id": {
                        "type": "string",
                        "description": "The Jira board ID"
                    },
                    "sprint_id": {
                        "type": "string",
                        "description": "Optional specific sprint ID"
                    }
                },
                "required": ["board_id"]
            }
        ),
        Tool(
            name="get_assignee",
            description="Get the assignee of a ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticket_key": {
                        "type": "string",
                        "description": "The Jira ticket key"
                    }
                },
                "required": ["ticket_key"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Jira tool."""
    
    # TODO: Replace with actual Jira API calls
    # For now, return mock data
    
    if name == "get_ticket":
        ticket_key = arguments.get("ticket_key", "UNKNOWN")
        return [TextContent(
            type="text",
            text=f"""
Ticket: {ticket_key}
Status: In Progress
Priority: High
Assignee: alice@company.com
Summary: Implement user authentication flow
Description: Add OAuth2 support with Google and GitHub providers.
Created: 2025-01-05
Updated: 2025-01-08
"""
        )]
    
    elif name == "search_tickets":
        jql = arguments.get("jql", "")
        return [TextContent(
            type="text",
            text=f"""
Search results for: {jql}

1. PROJ-123 - Implement authentication (In Progress)
2. PROJ-124 - Add dashboard widgets (To Do)
3. PROJ-125 - Fix login bug (Done)
"""
        )]
    
    elif name == "get_sprint_velocity":
        return [TextContent(
            type="text",
            text="""
Sprint: Sprint 23 (Current)
Velocity: 34 story points
Completed: 21 points
Remaining: 13 points
Team: 5 members
"""
        )]
    
    elif name == "get_assignee":
        ticket_key = arguments.get("ticket_key", "UNKNOWN")
        return [TextContent(
            type="text",
            text=f"Ticket {ticket_key} is assigned to alice@company.com"
        )]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-server-jira",
                server_version="0.1.0"
            )
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
