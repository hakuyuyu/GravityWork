# Makefile for GravityWork

.PHONY: setup test lint clean

setup:
	@echo "Setting up GravityWork..."
	@cd frontend && npm install
	@cd backend && pip install -r requirements.txt
	@docker-compose build

test:
	@echo "Running tests..."
	@cd backend && python -m pytest
	@cd frontend && npm test

lint:
	@echo "Running linters..."
	@cd backend && black --check .
	@cd backend && flake8 .
	@cd frontend && npx eslint .

clean:
	@echo "Cleaning up..."
	@rm -rf .pytest_cache
	@rm -rf __pycache__
	@rm -rf node_modules
	@rm -rf .env.local
	@rm -rf temp_files.txt
