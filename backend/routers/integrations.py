"""
Integrations router for GravityWork.
Manages connections to Jira, Slack, GitHub via MCP servers.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class IntegrationStatus(BaseModel):
    """Status of an integration."""
    name: str
    connected: bool
    last_sync: Optional[str] = None
    error: Optional[str] = None


class IntegrationConfig(BaseModel):
    """Configuration for an integration."""
    name: str
    credentials: Dict[str, str]


@router.get("/status")
async def get_integrations_status() -> Dict[str, IntegrationStatus]:
    """Get status of all integrations."""
    return {
        "jira": IntegrationStatus(
            name="Jira",
            connected=False,
            last_sync=None,
            error="Not configured"
        ),
        "slack": IntegrationStatus(
            name="Slack", 
            connected=False,
            last_sync=None,
            error="Not configured"
        ),
        "github": IntegrationStatus(
            name="GitHub",
            connected=False,
            last_sync=None,
            error="Not configured"
        ),
    }


@router.post("/connect/{integration_name}")
async def connect_integration(integration_name: str, config: IntegrationConfig):
    """Configure and connect an integration."""
    valid_integrations = ["jira", "slack", "github"]
    
    if integration_name not in valid_integrations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid integration. Must be one of: {valid_integrations}"
        )
    
    # TODO: Validate credentials and establish connection
    return {
        "status": "connected",
        "integration": integration_name,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.delete("/disconnect/{integration_name}")
async def disconnect_integration(integration_name: str):
    """Disconnect an integration."""
    return {
        "status": "disconnected",
        "integration": integration_name,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/test/{integration_name}")
async def test_integration(integration_name: str):
    """Test connectivity to an integration."""
    # TODO: Ping the MCP server
    return {
        "integration": integration_name,
        "reachable": False,
        "latency_ms": None,
        "error": "MCP server not running"
    }
