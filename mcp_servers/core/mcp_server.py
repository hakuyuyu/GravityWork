import logging
import threading
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import os
import signal
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class ServerConfig:
    """Configuration for MCP Server"""
    name: str
    host: str = "0.0.0.0"
    port: int = 8080
    env_prefix: str = "MCP"
    config_file: Optional[str] = None
    debug: bool = False

class MCPServer(ABC):
    """
    Base class for all MCP Servers.
    Provides common functionality for server lifecycle management.
    """

    def __init__(self, config: ServerConfig):
        """
        Initialize the MCP Server.

        Args:
            config: Server configuration
        """
        self.config = config
        self._running = False
        self._server_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()

        # Load configuration
        self._load_config()

        # Set up logging
        self._setup_logging()

        logger.info(f"Initializing MCP Server: {self.config.name}")
        logger.info(f"Configuration: {self._get_sanitized_config()}")

    def _load_config(self) -> None:
        """Load configuration from environment and config file"""
        # Load from environment variables
        self._load_env_config()

        # Load from config file if specified
        if self.config.config_file and os.path.exists(self.config.config_file):
            self._load_file_config()

    def _load_env_config(self) -> None:
        """Load configuration from environment variables"""
        prefix = self.config.env_prefix.upper()
        env_vars = {k: v for k, v in os.environ.items() if k.startswith(prefix)}

        for key, value in env_vars.items():
            logger.debug(f"Loaded env config: {key} = {value}")

    def _load_file_config(self) -> None:
        """Load configuration from JSON config file"""
        try:
            with open(self.config.config_file, 'r') as f:
                file_config = json.load(f)
                logger.debug(f"Loaded file config: {file_config}")
        except Exception as e:
            logger.error(f"Failed to load config file: {str(e)}")

    def _setup_logging(self) -> None:
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.DEBUG if self.config.debug else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _get_sanitized_config(self) -> Dict[str, Any]:
        """Get sanitized configuration for logging"""
        return {
            "name": self.config.name,
            "host": self.config.host,
            "port": self.config.port,
            "debug": self.config.debug
        }

    def start(self) -> None:
        """Start the server"""
        if self._running:
            logger.warning("Server is already running")
            return

        logger.info(f"Starting {self.config.name} server...")
        self._running = True
        self._shutdown_event.clear()

        # Start server in a separate thread
        self._server_thread = threading.Thread(
            target=self._run_server,
            daemon=True
        )
        self._server_thread.start()

        # Wait for server to be ready
        time.sleep(1)

        logger.info(f"{self.config.name} server started successfully")

    def stop(self) -> None:
        """Stop the server"""
        if not self._running:
            logger.warning("Server is not running")
            return

        logger.info(f"Stopping {self.config.name} server...")
        self._running = False
        self._shutdown_event.set()

        if self._server_thread:
            self._server_thread.join(timeout=5)
            if self._server_thread.is_alive():
                logger.warning("Server thread did not stop gracefully")

        logger.info(f"{self.config.name} server stopped")

    def restart(self) -> None:
        """Restart the server"""
        logger.info(f"Restarting {self.config.name} server...")
        self.stop()
        time.sleep(1)
        self.start()

    def _run_server(self) -> None:
        """Main server loop"""
        try:
            self._server_setup()
            self._server_main_loop()
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
        finally:
            self._server_cleanup()
            self._running = False

    @abstractmethod
    def _server_setup(self) -> None:
        """Server-specific setup logic"""
        pass

    @abstractmethod
    def _server_main_loop(self) -> None:
        """Main server loop implementation"""
        pass

    @abstractmethod
    def _server_cleanup(self) -> None:
        """Server cleanup logic"""
        pass

    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            "status": "healthy" if self._running else "stopped",
            "name": self.config.name,
            "timestamp": time.time()
        }

    def is_running(self) -> bool:
        """Check if server is running"""
        return self._running

    def register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown"""
        def handle_signal(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop()

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
