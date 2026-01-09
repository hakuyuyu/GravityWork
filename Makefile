.PHONY: help
help:
	@echo "Available commands:"
	@echo "  setup          - Install all dependencies"
	@echo "  dev            - Run development server"
	@echo "  test           - Run all tests"
	@echo "  backend        - Start backend server"
	@echo "  frontend       - Start frontend server"
	@echo "  qdrant         - Start Qdrant vector database"
	@echo "  mcp-jira       - Start Jira MCP server"
	@echo "  mcp-slack      - Start Slack MCP server"

.PHONY: setup
setup:
	./init.sh

.PHONY: dev
dev:
	docker-compose up --build

.PHONY: test
test:
	# Placeholder for tests
	@echo "No tests configured yet"

.PHONY: backend
backend:
	cd backend && source venv/bin/activate && uvicorn main:app --reload

.PHONY: frontend
frontend:
	cd frontend && npm run dev

.PHONY: qdrant
qdrant:
	docker-compose up qdrant

.PHONY: mcp-jira
mcp-jira:
	cd mcp-servers && uvicorn mcp_server_jira:app --reload

.PHONY: mcp-slack
mcp-slack:
	cd mcp-servers && python mcp_server_slack.py
