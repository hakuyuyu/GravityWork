.PHONY: build, up, down, test, clean

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

test:
	# Placeholder for tests
	@echo "Running tests..."

clean:
	docker-compose down -v
	rm -rf frontend/node_modules frontend/.next
	rm -rf backend/__pycache__
