#!/bin/bash

# Helper script to run docker compose with the appropriate configuration
# Usage: 
#   ./compose-up.sh        - Runs in production mode (using pre-built images)
#   ./compose-up.sh dev    - Runs in development mode (building locally)

# Determine if this is development or production mode
if [ "$1" == "dev" ]; then
  export BUILD_LOCALLY=true
  echo "Starting in DEVELOPMENT mode (building locally)"
  # For dev mode, we want to always rebuild
  docker compose up -d --build
else
  export BUILD_LOCALLY=false
  echo "Starting in PRODUCTION mode (using pre-built images)"
  # For production mode, just pull and run
  docker compose pull
  docker compose up -d
fi

echo ""
echo "Services are now running:"
echo "- Frontend: http://localhost:8081"
echo "- Backend: http://localhost:8000"
echo ""
echo "To stop all services: docker compose down"
