"""
MCP Server for Slack - GravityWork
Provides access to Slack messages, threads, and channel history.
"""

import os
from typing import Any
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("mcp-server-slack")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Slack tools."""
    return [
        Tool(
            name="get_thread",
            description="Get a Slack thread by URL or message ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {"type": "string", "description": "Slack channel ID"},
                    "thread_ts": {"type": "string", "description": "Thread timestamp"}
                },
                "required": ["channel_id", "thread_ts"]
            }
        ),
        Tool(
            name="search_messages",
            description="Search Slack messages",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "channel": {"type": "string", "description": "Optional channel filter"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_channel_history",
            description="Get recent messages from a channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 20}
                },
                "required": ["channel_id"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Slack tool."""
    
    if name == "get_thread":
        return [TextContent(
            type="text",
            text="""
Thread: Login Bug Discussion

@alice (Jan 7, 10:32 AM):
  Found the issue - the OAuth callback URL is incorrect in production.

@bob (Jan 7, 10:45 AM):
  Good catch! Can you create a ticket for this?

@alice (Jan 7, 10:48 AM):
  Done - PROJ-125
"""
        )]
    
    elif name == "search_messages":
        query = arguments.get("query", "")
        return [TextContent(
            type="text",
            text=f"""
Search results for "{query}":

1. #engineering (Jan 7): "The login bug is related to OAuth callback..."
2. #product (Jan 6): "Users reporting login issues on mobile..."
3. #alerts (Jan 5): "Error spike detected in auth service..."
"""
        )]
    
    elif name == "get_channel_history":
        return [TextContent(
            type="text",
            text="""
Recent messages in #engineering:

@alice (2h ago): Deployed fix for the login issue
@bob (3h ago): Code review done for PR #234
@charlie (5h ago): Sprint planning at 2pm today
"""
        )]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream,
            InitializationOptions(server_name="mcp-server-slack", server_version="0.1.0")
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
