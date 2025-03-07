#!/bin/bash
set -e

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
  DEFAULT_PROFILE="dev-x86"
elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
  DEFAULT_PROFILE="dev-arm64"
else
  echo "Unsupported architecture: $ARCH"
  echo "Please specify a profile manually: dev-x86, dev-arm64, prod-x86, or prod-arm64"
  exit 1
fi

# Variables
PROFILE=${1:-$DEFAULT_PROFILE}  # Default to architecture-specific dev profile if none specified
echo "Using profile: $PROFILE"

# Validate profile
if [[ ! "$PROFILE" =~ ^(dev-x86|dev-arm64|prod-x86|prod-arm64)$ ]]; then
  echo "Warning: '$PROFILE' is not a recognized profile name."
  echo "Available profiles: dev-x86, dev-arm64, prod-x86, prod-arm64"
  read -p "Continue with profile '$PROFILE'? (y/n): " CONFIRM
  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
  fi
fi

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
