from fastapi import FastAPI, HTTPException
from typing import Dict, Any
import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MCPConfig(BaseModel):
    server_name: str
    port: int = 8000

class MCPServer:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.config = MCPConfig(server_name=service_name)
        self.app = FastAPI(title=f"{service_name} MCP Server")

        # Add health check endpoint
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": self.service_name}

    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from the external service."""
        raise NotImplementedError("Subclasses must implement fetch_data")

    def start(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the MCP server."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)
