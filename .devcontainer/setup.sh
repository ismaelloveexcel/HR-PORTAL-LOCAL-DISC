#!/bin/bash
# ============================================
# HR Portal - Codespaces Setup Script
# ============================================
# This script runs automatically when a Codespace is created
# It installs all dependencies and configures the environment

set -e

echo ""
echo "============================================"
echo "   HR PORTAL - CODESPACES SETUP"
echo "============================================"
echo ""

# Install UV package manager
echo "[1/5] Installing UV package manager..."
pip install uv --quiet
echo "      ✓ UV installed"

# Find workspace directory (using CODESPACE_REPO_ROOT if available)
WORKSPACE_DIR="${CODESPACE_REPO_ROOT:-/workspaces/AZURE-DEPLOYMENT-HR-PORTAL}"
if [ ! -d "$WORKSPACE_DIR" ]; then
    WORKSPACE_DIR=$(find /workspaces -maxdepth 1 -type d -name "*HR-PORTAL*" 2>/dev/null | head -1)
fi
if [ ! -d "$WORKSPACE_DIR" ]; then
    WORKSPACE_DIR=$(find /workspaces -maxdepth 1 -type d ! -name "workspaces" 2>/dev/null | head -1)
fi

# Install backend dependencies
echo "[2/5] Installing backend dependencies..."
cd "$WORKSPACE_DIR/backend"
uv sync --quiet
echo "      ✓ Backend dependencies installed"

# Generate secure random key for development
RANDOM_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Configure backend environment
echo "[3/5] Configuring backend environment..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
APP_NAME=Secure Renewals API
APP_ENV=development
API_PREFIX=/api
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:5000

# SQLite database (perfect for Codespaces - no setup needed)
DATABASE_URL=sqlite:///./hr_portal.db

# Authentication - generated secure key
AUTH_SECRET_KEY=${RANDOM_SECRET}
SESSION_TIMEOUT_HOURS=8
PASSWORD_MIN_LENGTH=8
DEV_AUTH_BYPASS=false
EOF
fi
echo "      ✓ Backend configured"

# Setup database
echo "[4/5] Setting up database..."
uv run alembic upgrade head 2>/dev/null || echo "      Note: Migrations will run on first start"
echo "      ✓ Database ready"

# Install frontend dependencies
echo "[5/5] Installing frontend dependencies..."
cd "$WORKSPACE_DIR/frontend"
npm install --silent
echo "      ✓ Frontend dependencies installed"

echo ""
echo "============================================"
echo "   SETUP COMPLETE!"
echo "============================================"
echo ""
echo "   The application will start automatically."
echo ""
echo "   Access your private HR Portal at the URLs"
echo "   shown in the PORTS tab below."
echo ""
echo "============================================"
echo ""
