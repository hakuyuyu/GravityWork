"""
Slack MCP Server

Read-only interface for Slack API
"""

from typing import Dict, Any, Optional, List
from .base_mcp_server import MCPServer, MCPConfig
from pydantic import BaseModel
from fastapi import HTTPException, status
from datetime import datetime

class SlackMessage(BaseModel):
    """Represents a Slack message"""
    id: str
    channel: str
    text: str
    user: str
    timestamp: datetime
    thread_ts: Optional[str] = None
    reactions: Optional[List[Dict]] = None

class SlackChannel(BaseModel):
    """Represents a Slack channel"""
    id: str
    name: str
    is_channel: bool
    is_group: bool
    is_im: bool
    created: datetime
    creator: str

class SlackUser(BaseModel):
    """Represents a Slack user"""
    id: str
    name: str
    real_name: str
    email: Optional[str] = None
    is_bot: bool

class SlackMCPServer(MCPServer):
    """Slack MCP Server implementation"""

    def __init__(self, config: MCPConfig):
        """
        Initialize Slack MCP Server

        Args:
            config: Configuration for the server
        """
        super().__init__(config)
        self._setup_slack_routes()

    def _setup_slack_routes(self):
        """Setup Slack-specific routes"""

        @self.app.get("/messages/{channel_id}")
        async def get_messages(
            channel_id: str,
            limit: int = 100,
            oldest: Optional[float] = None,
            latest: Optional[float] = None
        ):
            """
            Get messages from a Slack channel

            Args:
                channel_id: Slack channel ID
                limit: Maximum number of messages to return
                oldest: Oldest timestamp to include
                latest: Latest timestamp to include

            Returns:
                List of SlackMessage objects
            """
            try:
                params = {
                    "channel": channel_id,
                    "limit": limit
                }

                if oldest:
                    params["oldest"] = oldest
                if latest:
                    params["latest"] = latest

                messages_data = self._make_request(
                    "GET",
                    "conversations.history",
                    params=params
                )

                messages = []
                for message in messages_data["messages"]:
                    if "text" not in message:
                        continue

                    messages.append({
                        "id": message["ts"],
                        "channel": channel_id,
                        "text": message["text"],
                        "user": message.get("user", "unknown"),
                        "timestamp": datetime.fromtimestamp(float(message["ts"])),
                        "thread_ts": message.get("thread_ts"),
                        "reactions": message.get("reactions")
                    })

                return {
                    "channel": channel_id,
                    "messages": messages,
                    "has_more": messages_data.get("has_more", False)
                }

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch Slack messages: {str(e)}"
                )

        @self.app.get("/channels")
        async def get_channels(
            exclude_archived: bool = True,
            limit: int = 1000
        ):
            """
            Get list of Slack channels

            Args:
                exclude_archived: Exclude archived channels
                limit: Maximum number of channels to return

            Returns:
                List of SlackChannel objects
            """
            try:
                channels_data = self._make_request(
                    "GET",
                    "conversations.list",
                    params={
                        "types": "public_channel,private_channel",
                        "exclude_archived": str(exclude_archived).lower(),
                        "limit": limit
                    }
                )

                channels = []
                for channel in channels_data["channels"]:
                    channels.append({
                        "id": channel["id"],
                        "name": channel["name"],
                        "is_channel": channel["is_channel"],
                        "is_group": channel["is_group"],
                        "is_im": channel["is_im"],
                        "created": datetime.fromtimestamp(float(channel["created"])),
                        "creator": channel["creator"]
                    })

                return {
                    "channels": channels,
                    "total": len(channels)
                }

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch Slack channels: {str(e)}"
                )

        @self.app.get("/users")
        async def get_users(limit: int = 1000):
            """
            Get list of Slack users

            Args:
                limit: Maximum number of users to return

            Returns:
                List of SlackUser objects
            """
            try:
                users_data = self._make_request(
                    "GET",
                    "users.list",
                    params={"limit": limit}
                )

                users = []
                for user in users_data["members"]:
                    if user["deleted"] or user["is_bot"]:
                        continue

                    users.append({
                        "id": user["id"],
                        "name": user["name"],
                        "real_name": user["real_name"],
                        "email": user.get("profile", {}).get("email"),
                        "is_bot": user["is_bot"]
                    })

                return {
                    "users": users,
                    "total": len(users)
                }

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch Slack users: {str(e)}"
                )

        @self.app.get("/channels/{channel_id}/info")
        async def get_channel_info(channel_id: str):
            """
            Get information about a specific Slack channel

            Args:
                channel_id: Slack channel ID

            Returns:
                SlackChannel object
            """
            try:
                channel_data = self._make_request(
                    "GET",
                    "conversations.info",
                    params={"channel": channel_id}
                )

                channel = channel_data["channel"]
                return {
                    "id": channel["id"],
                    "name": channel["name"],
                    "is_channel": channel["is_channel"],
                    "is_group": channel["is_group"],
                    "is_im": channel["is_im"],
                    "created": datetime.fromtimestamp(float(channel["created"])),
                    "creator": channel["creator"]
                }

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch Slack channel info: {str(e)}"
                )

def create_slack_server() -> SlackMCPServer:
    """Factory function to create a Slack MCP Server"""
    config = MCPConfig(
        server_name="Slack",
        api_base_url=os.getenv("SLACK_API_BASE_URL", "https://slack.com/api"),
        api_key=os.getenv("SLACK_API_KEY")
    )
    return SlackMCPServer(config)

# Create server instance
slack_server = create_slack_server()
app = slack_server.get_app()
