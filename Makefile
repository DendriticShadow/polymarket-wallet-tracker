.PHONY: help install dev-install run-api run-collector run-detector docker-up docker-down docker-logs test clean

help:
	@echo "Polymarket Tracker - Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make dev-install    - Install dev dependencies and setup"
	@echo "  make run-api        - Run API server"
	@echo "  make run-collector  - Run data collector"
	@echo "  make run-detector   - Run pattern detector"
	@echo "  make docker-up      - Start all services with Docker"
	@echo "  make docker-down    - Stop all Docker services"
	@echo "  make docker-logs    - View Docker logs"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up cache files"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	cp .env.example .env
	@echo "✓ Installed dependencies"
	@echo "✓ Created .env file - please update with your settings"

run-api:
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-collector:
	python scripts/collector.py

run-detector:
	python scripts/detector.py

docker-up:
	docker-compose up -d
	@echo "✓ Services started"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

test:
	pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
