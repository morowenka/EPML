#!/bin/bash
set -e

# Script to setup ClearML Server using Docker Compose

echo "Setting up ClearML Server..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "Error: Docker and docker-compose are required but not installed."
    exit 1
fi

# Use docker compose (v2) if available, otherwise docker-compose (v1)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "Error: docker-compose is not available."
    exit 1
fi

# Start ClearML Server
echo "Starting ClearML Server services..."
$DOCKER_COMPOSE up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
if $DOCKER_COMPOSE ps | grep -q "Up"; then
    echo "✓ ClearML Server is starting up..."
    echo ""
    echo "Services status:"
    $DOCKER_COMPOSE ps
    echo ""
    echo "ClearML Web UI will be available at: http://localhost:8080"
    echo "File Server will be available at: http://localhost:8081"
    echo ""
    echo "To view logs: $DOCKER_COMPOSE logs -f"
    echo "To stop services: $DOCKER_COMPOSE down"
    echo ""
    echo "Next steps:"
    echo "1. Wait for all services to be healthy (check with: $DOCKER_COMPOSE ps)"
    echo "2. Open http://localhost:8080 in your browser"
    echo "3. Create an account (first user becomes admin)"
    echo "4. Get your API credentials from the profile page"
    echo "5. Run: python scripts/create_clearml_project.py"
else
    echo "Error: Failed to start services. Check logs with: $DOCKER_COMPOSE logs"
    exit 1
fi

