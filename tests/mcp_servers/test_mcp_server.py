import unittest
import time
import threading
from mcp_servers.core.mcp_server import MCPServer, ServerConfig
from mcp_servers.example_server import ExampleServer
from mcp_servers.server_factory import ServerFactory

class TestMCPServer(unittest.TestCase):
    """Tests for MCP Server base class"""

    def setUp(self):
        self.config = ServerConfig(
            name="test_server",
            host="0.0.0.0",
            port=8081,
            debug=True
        )

    def test_server_initialization(self):
        """Test server initialization"""
        server = ExampleServer(self.config)
        self.assertEqual(server.config.name, "test_server")
        self.assertFalse(server.is_running())

    def test_server_lifecycle(self):
        """Test server start/stop lifecycle"""
        server = ExampleServer(self.config)

        # Test start
        server.start()
        self.assertTrue(server.is_running())

        # Test health check
        health = server.health_check()
        self.assertEqual(health["status"], "healthy")

        # Test stop
        server.stop()
        self.assertFalse(server.is_running())

    def test_server_restart(self):
        """Test server restart"""
        server = ExampleServer(self.config)

        server.start()
        self.assertTrue(server.is_running())

        server.restart()
        self.assertTrue(server.is_running())

        server.stop()

    def test_server_factory(self):
        """Test server factory"""
        # Test available servers
        available = ServerFactory.get_available_servers()
        self.assertIn("example", available)

        # Test server creation
        server = ServerFactory.create_server("example", self.config)
        self.assertIsInstance(server, ExampleServer)

        # Test unknown server type
        with self.assertRaises(ValueError):
            ServerFactory.create_server("unknown", self.config)

if __name__ == "__main__":
    unittest.main()
