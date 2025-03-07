#!/bin/bash
set -e

# Variables
PROFILE=${1:-dev}  # Default to dev profile if none specified
echo "Using profile: $PROFILE"

# Stop any existing containers
echo "Stopping existing containers..."
docker compose --profile "$PROFILE" down

# Rebuild images from source (needed to incorporate our changes)
echo "Rebuilding images..."
docker compose --profile "$PROFILE" build

# Start the services
echo "Starting services..."
docker compose --profile "$PROFILE" up -d

# Check if services are running
echo "Waiting for services to start..."
sleep 3
docker compose ps

echo "Application should now be accessible at http://localhost:8081"
echo "Check browser console for debugging information (F12 > Console)"
