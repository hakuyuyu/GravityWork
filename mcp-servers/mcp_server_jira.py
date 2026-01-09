"""
Jira MCP Server

Read-only interface for Jira API
"""

from typing import Dict, Any, Optional, List
from .base_mcp_server import MCPServer, MCPConfig
from pydantic import BaseModel
from fastapi import HTTPException, status
from datetime import datetime

class JiraIssue(BaseModel):
    """Represents a Jira issue"""
    id: str
    key: str
    summary: str
    description: Optional[str] = None
    status: str
    issue_type: str
    created: datetime
    updated: datetime
    priority: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None

class JiraProject(BaseModel):
    """Represents a Jira project"""
    id: str
    key: str
    name: str
    description: Optional[str] = None

class JiraMCPServer(MCPServer):
    """Jira MCP Server implementation"""

    def __init__(self, config: MCPConfig):
        """
        Initialize Jira MCP Server

        Args:
            config: Configuration for the server
        """
        super().__init__(config)
        self._setup_jira_routes()

    def _setup_jira_routes(self):
        """Setup Jira-specific routes"""

        @self.app.get("/issues/{issue_key}")
        async def get_issue(issue_key: str):
            """
            Get a specific Jira issue

            Args:
                issue_key: Jira issue key (e.g., PROJ-123)

            Returns:
                JiraIssue object
            """
            try:
                issue_data = self._make_request(
                    "GET",
                    f"rest/api/2/issue/{issue_key}",
                    params={"fields": "summary,description,status,issuetype,created,updated,priority,assignee,reporter"}
                )

                return {
                    "id": issue_data["id"],
                    "key": issue_data["key"],
                    "summary": issue_data["fields"]["summary"],
                    "description": issue_data["fields"].get("description"),
                    "status": issue_data["fields"]["status"]["name"],
                    "issue_type": issue_data["fields"]["issuetype"]["name"],
                    "created": issue_data["fields"]["created"],
                    "updated": issue_data["fields"]["updated"],
                    "priority": issue_data["fields"]["priority"]["name"] if issue_data["fields"].get("priority") else None,
                    "assignee": issue_data["fields"]["assignee"]["displayName"] if issue_data["fields"].get("assignee") else None,
                    "reporter": issue_data["fields"]["reporter"]["displayName"] if issue_data["fields"].get("reporter") else None
                }

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch Jira issue: {str(e)}"
                )

        @self.app.get("/projects/{project_key}")
        async def get_project(project_key: str):
            """
            Get a specific Jira project

            Args:
                project_key: Jira project key

            Returns:
                JiraProject object
            """
            try:
                project_data = self._make_request(
                    "GET",
                    f"rest/api/2/project/{project_key}"
                )

                return {
                    "id": project_data["id"],
                    "key": project_data["key"],
                    "name": project_data["name"],
                    "description": project_data.get("description")
                }

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch Jira project: {str(e)}"
                )

        @self.app.get("/issues")
        async def search_issues(
            jql: Optional[str] = None,
            project_key: Optional[str] = None,
            status: Optional[str] = None,
            limit: int = 50
        ):
            """
            Search for Jira issues

            Args:
                jql: JQL query string
                project_key: Filter by project key
                status: Filter by status
                limit: Maximum number of results

            Returns:
                List of JiraIssue objects
            """
            try:
                # Build JQL query
                jql_parts = []
                if jql:
                    jql_parts.append(jql)
                if project_key:
                    jql_parts.append(f"project = {project_key}")
                if status:
                    jql_parts.append(f"status = '{status}'")

                query = " AND ".join(jql_parts) if jql_parts else ""

                search_data = self._make_request(
                    "GET",
                    "rest/api/2/search",
                    params={
                        "jql": query,
                        "fields": "summary,description,status,issuetype,created,updated,priority,assignee,reporter",
                        "maxResults": limit
                    }
                )

                issues = []
                for issue in search_data["issues"]:
                    issues.append({
                        "id": issue["id"],
                        "key": issue["key"],
                        "summary": issue["fields"]["summary"],
                        "description": issue["fields"].get("description"),
                        "status": issue["fields"]["status"]["name"],
                        "issue_type": issue["fields"]["issuetype"]["name"],
                        "created": issue["fields"]["created"],
                        "updated": issue["fields"]["updated"],
                        "priority": issue["fields"]["priority"]["name"] if issue["fields"].get("priority") else None,
                        "assignee": issue["fields"]["assignee"]["displayName"] if issue["fields"].get("assignee") else None,
                        "reporter": issue["fields"]["reporter"]["displayName"] if issue["fields"].get("reporter") else None
                    })

                return {
                    "total": search_data["total"],
                    "issues": issues
                }

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to search Jira issues: {str(e)}"
                )

def create_jira_server() -> JiraMCPServer:
    """Factory function to create a Jira MCP Server"""
    config = MCPConfig(
        server_name="Jira",
        api_base_url=os.getenv("JIRA_API_BASE_URL"),
        api_key=os.getenv("JIRA_API_KEY")
    )
    return JiraMCPServer(config)

# Create server instance
jira_server = create_jira_server()
app = jira_server.get_app()
