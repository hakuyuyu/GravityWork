"""
Base MCP (Message Control Protocol) Server Template

This module provides the foundation for all MCP servers, which are responsible
for interfacing with external systems (Jira, Slack, etc.) and providing
read-only access to their data.
"""

import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPConfig(BaseModel):
    """Configuration for MCP Server"""
    server_name: str
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

class MCPServer:
    """Base class for all MCP Servers"""

    def __init__(self, config: MCPConfig):
        """
        Initialize the MCP Server

        Args:
            config: Configuration for the server
        """
        self.config = config
        self.app = FastAPI(
            title=f"{config.server_name} MCP Server",
            description=f"Read-only interface for {config.server_name}",
            version="1.0.0"
        )

        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup all API routes for the server"""
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "server": self.config.server_name,
                "timestamp": datetime.utcnow().isoformat()
            }

        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "message": f"{self.config.server_name} MCP Server",
                "status": "running",
                "version": "1.0.0"
            }

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                     headers: Optional[Dict] = None, data: Optional[Dict] = None) -> Any:
        """
        Make an HTTP request to the external API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            headers: Request headers
            data: Request body

        Returns:
            Response data

        Raises:
            HTTPException: If request fails
        """
        if not self.config.api_base_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API base URL not configured"
            )

        url = f"{self.config.api_base_url}/{endpoint}"
        headers = headers or {}
        params = params or {}

        # Add authentication if API key is provided
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        retry_count = 0
        last_exception = None

        while retry_count < self.config.max_retries:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=headers,
                    json=data,
                    timeout=self.config.timeout
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Unauthorized access to external API"
                    )
                elif response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Resource not found"
                    )
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"External API error: {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                last_exception = e
                retry_count += 1
                if retry_count < self.config.max_retries:
                    logger.warning(f"Request failed, retry {retry_count}/{self.config.max_retries}: {str(e)}")
                    continue
                else:
                    logger.error(f"Request failed after {self.config.max_retries} retries: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"External API unavailable: {str(e)}"
                    ) from e

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Request failed: {str(last_exception)}"
        ) from last_exception

    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance"""
        return self.app

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the server (for development only)"""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)
