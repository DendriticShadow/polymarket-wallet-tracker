#!/bin/bash

# Polymarket Tracker - Quick Start Script

set -e

echo "=================================="
echo "Polymarket Tracker - Quick Start"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    echo "Please install docker-compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker is installed"
echo "✓ docker-compose is installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
fi

# Start services
echo "Starting services with Docker Compose..."
echo ""
docker-compose up -d

echo ""
echo "=================================="
echo "Services Started Successfully!"
echo "=================================="
echo ""
echo "📊 API Server:        http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🗄️  PostgreSQL:        localhost:5432"
echo "📦 Redis:             localhost:6379"
echo ""
echo "Background services:"
echo "  ✓ Data Collector - Fetching Polymarket data"
echo "  ✓ Pattern Detector - Analyzing for suspicious activity"
echo ""
echo "=================================="
echo "Useful Commands:"
echo "=================================="
echo ""
echo "View logs:          docker-compose logs -f"
echo "Stop services:      docker-compose down"
echo "Restart services:   docker-compose restart"
echo "Check status:       docker-compose ps"
echo ""
echo "View API docs:      open http://localhost:8000/docs"
echo "Check health:       curl http://localhost:8000/health"
echo ""
echo "Wait a few minutes for data collection to begin..."
echo "Then check alerts:  curl http://localhost:8000/api/alerts"
echo ""
