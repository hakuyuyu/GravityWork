"""
Health check endpoints for GravityWork.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    services: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns status of the API and connected services.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "api": {"status": "up"},
            "qdrant": {"status": "pending"},  # Will be updated when connected
            "mcp_jira": {"status": "pending"},
            "mcp_slack": {"status": "pending"},
            "mcp_github": {"status": "pending"},
        }
    )


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"alive": True}
