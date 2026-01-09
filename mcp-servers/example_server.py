import logging
import time
from typing import Dict, Any
from .core.mcp_server import MCPServer, ServerConfig

logger = logging.getLogger(__name__)

class ExampleServer(MCPServer):
    """
    Example implementation of an MCP Server.
    Demonstrates basic functionality.
    """

    def __init__(self, config: ServerConfig):
        super().__init__(config)
        self.counter = 0

    def _server_setup(self) -> None:
        """Example server setup"""
        logger.info("Example server setup complete")
        self.counter = 0

    def _server_main_loop(self) -> None:
        """Example server main loop"""
        logger.info("Example server main loop started")
        while self.is_running() and not self._shutdown_event.is_set():
            self.counter += 1
            if self.counter % 10 == 0:
                logger.info(f"Example server running - counter: {self.counter}")
            time.sleep(1)

    def _server_cleanup(self) -> None:
        """Example server cleanup"""
        logger.info(f"Example server cleanup - final counter: {self.counter}")

    def get_status(self) -> Dict[str, Any]:
        """Get server status"""
        return {
            **self.health_check(),
            "counter": self.counter,
            "message": "Example server is running"
        }

# Example usage
if __name__ == "__main__":
    config = ServerConfig(
        name="example_server",
        host="0.0.0.0",
        port=8080,
        debug=True
    )

    server = ExampleServer(config)
    server.register_signal_handlers()

    try:
        server.start()

        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
