#!/bin/bash
# ============================================
# HR Portal - Codespaces Start Script
# ============================================
# This script runs automatically when a Codespace starts
# It starts both the backend and frontend servers

echo ""
echo "============================================"
echo "   HR PORTAL - STARTING APPLICATION"
echo "============================================"
echo ""

# Find workspace directory using multiple methods
WORKSPACE_DIR="${CODESPACE_REPO_ROOT:-/workspaces/AZURE-DEPLOYMENT-HR-PORTAL}"
if [ -z "$WORKSPACE_DIR" ] || [ ! -d "$WORKSPACE_DIR" ]; then
    WORKSPACE_DIR=$(find /workspaces -maxdepth 1 -type d -name "*HR-PORTAL*" 2>/dev/null | head -1)
fi
if [ -z "$WORKSPACE_DIR" ] || [ ! -d "$WORKSPACE_DIR" ]; then
    WORKSPACE_DIR=$(find /workspaces -maxdepth 1 -type d ! -name "workspaces" 2>/dev/null | head -1)
fi
if [ -z "$WORKSPACE_DIR" ] || [ ! -d "$WORKSPACE_DIR/backend" ]; then
    echo "ERROR: Could not find workspace directory"
    exit 1
fi

echo "   Workspace: $WORKSPACE_DIR"

# Start backend in background
echo "[1/2] Starting backend server..."
cd "$WORKSPACE_DIR/backend"

# Ensure database is ready
if [ ! -f "hr_portal.db" ]; then
    uv run alembic upgrade head 2>/dev/null || true
fi

# Start backend
nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
echo "      ✓ Backend starting on port 8000"

# Wait for backend to be ready using the public health endpoint
echo "      Waiting for backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health/db > /dev/null 2>&1; then
        echo "      ✓ Backend is ready!"
        break
    fi
    sleep 1
done

# Start frontend in background
echo "[2/2] Starting frontend server..."
cd "$WORKSPACE_DIR/frontend"
nohup npm run dev > /tmp/frontend.log 2>&1 &
echo "      ✓ Frontend starting on port 5000"

# Wait for frontend
echo "      Waiting for frontend..."
sleep 5

echo ""
echo "============================================"
echo "   HR PORTAL IS RUNNING!"
echo "============================================"
echo ""
echo "   🔒 Your private HR Portal is ready!"
echo ""
echo "   Check the PORTS tab below to access:"
echo "   • Port 5000 - HR Portal (Frontend)"
echo "   • Port 8000 - API Documentation"
echo ""
echo "   URLs are PRIVATE - only you can access them."
echo "   The URL looks like: xxx-5000.app.github.dev"
echo ""
echo "   Default admin login:"
echo "   • Employee ID: BAYN00008"
echo "   • Password: Your date of birth (DDMMYYYY)"
echo ""
echo "============================================"
echo ""
echo "   Logs: /tmp/backend.log, /tmp/frontend.log"
echo ""
