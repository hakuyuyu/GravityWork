import logging
from typing import Type, Dict, Any
from .core.mcp_server import MCPServer, ServerConfig
from .example_server import ExampleServer

logger = logging.getLogger(__name__)

class ServerFactory:
    """
    Factory for creating MCP Server instances.
    """

    _server_types: Dict[str, Type[MCPServer]] = {
        "example": ExampleServer
    }

    @classmethod
    def register_server_type(cls, server_type: str, server_class: Type[MCPServer]) -> None:
        """Register a new server type"""
        cls._server_types[server_type] = server_class
        logger.info(f"Registered server type: {server_type}")

    @classmethod
    def create_server(cls, server_type: str, config: ServerConfig) -> MCPServer:
        """
        Create a server instance.

        Args:
            server_type: Type of server to create
            config: Server configuration

        Returns:
            Instance of the requested server

        Raises:
            ValueError: If server type is not registered
        """
        if server_type not in cls._server_types:
            raise ValueError(f"Unknown server type: {server_type}. Available types: {list(cls._server_types.keys())}")

        server_class = cls._server_types[server_type]
        return server_class(config)

    @classmethod
    def get_available_servers(cls) -> Dict[str, str]:
        """Get available server types"""
        return {name: cls.__name__ for name, cls in cls._server_types.items()}
