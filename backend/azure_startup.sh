#!/bin/bash
# Azure App Service startup script for HR Portal
# This script is executed by Azure App Service to start the FastAPI application

echo "=== HR Portal Azure Startup ==="
echo "Timestamp: $(date)"
echo "PORT: ${PORT:-8000}"
echo "PWD: $(pwd)"

# Navigate to app directory
cd /home/site/wwwroot || exit 1

# Activate virtual environment (Oryx creates 'antenv', fallback to .venv)
if [ -d "antenv" ] && [ -f "antenv/bin/activate" ]; then
    echo "Activating Oryx virtual environment (antenv)..."
    source antenv/bin/activate
elif [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
    echo "Activating .venv virtual environment..."
    source .venv/bin/activate
else
    echo "No virtual environment found, using system Python..."
    # Install dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        echo "Installing Python dependencies..."
        pip install -r requirements.txt --quiet 2>/dev/null || echo "Warning: pip install had issues"
    fi
fi

# Log Python and package info for debugging
echo "Python: $(python --version 2>&1)"
echo "Uvicorn: $(python -m pip show uvicorn 2>/dev/null | grep Version || echo 'not found')"

# Start the FastAPI application
# Use $PORT environment variable (provided by Azure App Service)
echo "Starting FastAPI application on port ${PORT:-8000}..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
