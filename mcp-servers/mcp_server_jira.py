from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import logging

app = FastAPI()

class JiraRequest(BaseModel):
    project_id: str
    query: str

class JiraResponse(BaseModel):
    tickets: list
    error: Optional[str] = None

@app.post("/mcp/jira", response_model=JiraResponse)
async def get_jira_tickets(request: JiraRequest):
    """
    Endpoint for fetching Jira tickets.

    Args:
        request: JiraRequest containing the project_id and query.

    Returns:
        JiraResponse containing the list of tickets or error.
    """
    try:
        # Simulate Jira API call (replace with actual Jira API integration)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://jira.example.com/rest/api/2/search",
                params={"jql": f"project={request.project_id} AND text ~ '{request.query}'"}
            )
            response.raise_for_status()
            tickets = response.json().get("issues", [])

        return JiraResponse(tickets=tickets)

    except Exception as e:
        logging.error(f"Error fetching Jira tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))
