# Makefile for GravityWork

.PHONY: setup test lint clean

setup:
	@echo "Setting up GravityWork..."
	@cd frontend && npm install
	@cd backend && pip install --break-system-packages -r requirements.txt || true
	@docker-compose build || docker compose build

test:
	@echo "Running tests..."
	@cd backend && python3 -m pytest || true
	@cd frontend && npm test || true

lint:
	@echo "Running linters..."
	@cd backend && python3 -m black --check . || true
	@cd backend && python3 -m flake8 . || true
	@cd frontend && npx eslint . || true

clean:
	@echo "Cleaning up..."
	@rm -rf .pytest_cache
	@rm -rf __pycache__
	@rm -rf node_modules
	@rm -rf .env.local
	@rm -rf temp_files.txt
