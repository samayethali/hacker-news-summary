#!/bin/bash
set -e

# Wait for any dependent services if needed
# Example: wait for a database
# while ! nc -z db 5432; do
#   echo "Waiting for database to be ready..."
#   sleep 2
# done

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "Warning: ANTHROPIC_API_KEY environment variable is not set"
  echo "The application may not function correctly without this key"
fi

# Execute the provided command (CMD from Dockerfile)
exec "$@"
