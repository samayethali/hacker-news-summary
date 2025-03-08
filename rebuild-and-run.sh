#!/bin/bash
set -e

# Detect architecture (informational only - the compose setup now handles this automatically)
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"
echo "Note: This application now uses multi-architecture images that work on any system"

# Determine mode (development or production)
if [ "$1" == "production" ] || [ "$1" == "prod" ]; then
  MODE=""
  echo "Using production mode (pre-built images)"
else
  MODE="dev"
  echo "Using development mode (building locally)"
fi

# Stop any existing containers
echo "Stopping existing containers..."
docker compose down

# Clean up any old containers/images to ensure a fresh start
echo "Pruning unused containers..."
docker container prune -f
echo "Pruning unused images..."
docker image prune -f

# Use the run.sh helper script to rebuild and start services
echo "Rebuilding and starting services..."
./run.sh $MODE

# Check if services are running
echo "Waiting for services to start..."
sleep 3
docker compose ps

echo "Application should now be accessible at http://localhost:8081"
echo "Check browser console for debugging information (F12 > Console)"
