#!/bin/bash

# Startup script for Railway deployment
# Properly handles PORT environment variable

# Set default port if not provided
PORT=${PORT:-8000}

echo "Starting application on port $PORT"

# Start uvicorn with the PORT variable
exec uvicorn chat.app:app --host 0.0.0.0 --port "$PORT"
