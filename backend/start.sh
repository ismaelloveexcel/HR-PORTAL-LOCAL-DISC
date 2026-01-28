#!/bin/bash
# Production startup script that uses PORT environment variable
# Uses gunicorn with uvicorn workers for better process management
PORT="${PORT:-5000}"
WORKERS="${WORKERS:-4}"

# Check if gunicorn is available (production), otherwise fall back to uvicorn (development)
if command -v gunicorn &> /dev/null; then
    exec gunicorn -w $WORKERS -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
else
    exec uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT
fi
