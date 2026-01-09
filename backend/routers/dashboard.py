from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.services.mcp_client import get_mcp_client
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stats")
async def get_dashboard_stats():
    """
    Get aggregated dashboard statistics.
    """
    try:
        client = get_mcp_client()
        # Fetch all issues (using search with empty query to get everything)
        result = await client.search_tickets("")
        
        if not result.success:
            raise HTTPException(status_code=500, detail=f"Failed to fetch Jira data: {result.error}")
        
        issues = result.data.get("data", {}).get("issues", [])
        
        # Calculate metrics
        total = len(issues)
        active = sum(1 for i in issues if i["status"] in ["Open", "In Progress", "To Do"])
        completed = sum(1 for i in issues if i["status"] in ["Done", "Closed", "Resolved"])
        blocked = sum(1 for i in issues if i["status"] in ["Blocked", "Flagged"])
        
        # Simple velocity calculation (just completed count for now)
        velocity = completed * 3 # Assume 3 SP per ticket avg
        
        return {
            "velocity": {
                "value": f"{velocity} SP",
                "trend": "+12%", # Mock trend
                "trend_direction": "up"
            },
            "active_tickets": {
                "value": active,
                "label": "Active Issues"
            },
            "attention_needed": {
                "value": blocked,
                "label": "Blocked/Flagged",
                "status": "warning" if blocked > 0 else "success"
            },
            "completion_rate": int((completed / total * 100)) if total > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        # Return safe defaults if backend fails
        return {
            "velocity": {"value": "--", "trend": "0%"},
            "active_tickets": {"value": 0},
            "attention_needed": {"value": 0}
        }

@router.get("/activity")
async def get_activity_feed():
    """
    Get recent activity.
    """
    # Mock activity for now (could come from GitHub/Jira MCPs)
    return {
        "activities": [
            {
                "id": 1,
                "project": "PROJ-3",
                "action": "moved to In Progress",
                "time": "2h ago",
                "type": "jira"
            },
            {
                "id": 2,
                "project": "PROJ-2",
                "action": "marked as Done",
                "time": "4h ago",
                "type": "jira"
            },
            {
                "id": 3,
                "project": "frontend",
                "action": "commit: fix layout bug",
                "time": "5h ago",
                "type": "github"
            }
        ]
    }
