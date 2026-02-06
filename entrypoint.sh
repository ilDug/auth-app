#!/bin/sh
set -e

if [ "$MODE" = "DEVELOPMENT" ]; then
    echo "Starting FastAPI in DEVELOPMENT mode..."
    exec uv run fastapi dev main.py --host 0.0.0.0 --port 8000
else
    echo "Starting FastAPI in PRODUCTION mode..."
    exec uv run fastapi run main.py --host 0.0.0.0 --port 8000
fi
