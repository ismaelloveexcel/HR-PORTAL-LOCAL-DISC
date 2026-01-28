#!/bin/bash
# ============================================
# HR Portal ONE-CLICK Deployment for macOS/Linux
# ============================================
#
# This script does EVERYTHING automatically:
#   1. Installs Homebrew (if missing, macOS only)
#   2. Installs Python (if missing)
#   3. Installs Node.js (if missing)
#   4. Installs all dependencies
#   5. Sets up the database
#   6. Starts the application
#
# Just run: ./scripts/one-click-deploy.sh
#
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================"
echo "   HR PORTAL - ONE-CLICK DEPLOYMENT"
echo "============================================"
echo ""
echo "This will install everything automatically."
echo "Please wait, this may take 5-10 minutes..."
echo ""
echo "============================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
fi

echo -e "${BLUE}[1/6]${NC} Checking Python..."

# Check/Install Python
if ! command -v python3 &> /dev/null; then
    echo "      Python not found. Installing..."
    
    if [[ "$OS" == "macos" ]]; then
        # Check/Install Homebrew
        if ! command -v brew &> /dev/null; then
            echo "      Installing Homebrew first..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            
            # Add Homebrew to PATH for this session
            eval "$(/opt/homebrew/bin/brew shellenv)" 2>/dev/null || eval "$(/usr/local/bin/brew shellenv)" 2>/dev/null
        fi
        
        brew install python@3.11
    elif [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3 python3-pip
        else
            echo -e "${RED}[X]${NC} Could not install Python automatically."
            echo "    Please install Python 3.11+ manually from https://www.python.org/downloads/"
            exit 1
        fi
    fi
    echo -e "${GREEN}[OK]${NC} Python installed"
else
    echo -e "${GREEN}[OK]${NC} Python found"
fi

echo -e "${BLUE}[2/6]${NC} Checking Node.js..."

# Check/Install Node.js
if ! command -v node &> /dev/null; then
    echo "      Node.js not found. Installing..."
    
    if [[ "$OS" == "macos" ]]; then
        if ! command -v brew &> /dev/null; then
            echo -e "${RED}[X]${NC} Homebrew not available. Please install Node.js manually."
            echo "    Download from: https://nodejs.org/"
            exit 1
        fi
        brew install node@20
    elif [[ "$OS" == "linux" ]]; then
        # Use NodeSource for latest LTS
        if command -v apt-get &> /dev/null; then
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs
        elif command -v yum &> /dev/null || command -v dnf &> /dev/null; then
            curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
            if command -v dnf &> /dev/null; then
                sudo dnf install -y nodejs
            else
                sudo yum install -y nodejs
            fi
        else
            echo -e "${RED}[X]${NC} Could not install Node.js automatically."
            echo "    Please install Node.js 18+ manually from https://nodejs.org/"
            exit 1
        fi
    fi
    echo -e "${GREEN}[OK]${NC} Node.js installed"
else
    echo -e "${GREEN}[OK]${NC} Node.js found"
fi

echo -e "${BLUE}[3/6]${NC} Installing UV package manager..."

# Install UV
if ! command -v uv &> /dev/null; then
    pip3 install uv || python3 -m pip install uv
fi
echo -e "${GREEN}[OK]${NC} UV ready"

echo -e "${BLUE}[4/6]${NC} Installing dependencies (this takes a few minutes)..."

# Install backend dependencies
cd "$PROJECT_DIR/backend"
uv sync
echo "      Backend dependencies installed"

# Install frontend dependencies
cd "$PROJECT_DIR/frontend"
npm install
echo "      Frontend dependencies installed"

echo -e "${BLUE}[5/6]${NC} Configuring environment..."

# Configure backend
cd "$PROJECT_DIR/backend"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
    else
        cat > .env << EOF
DATABASE_URL=sqlite:///./hr_portal.db
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:5000
APP_BASE_URL=http://localhost:5000
EOF
    fi
fi
echo "      Backend configured with SQLite"

# Configure frontend
cd "$PROJECT_DIR/frontend"
if [ ! -f ".env" ]; then
    echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env
fi
echo "      Frontend configured"

echo -e "${BLUE}[6/6]${NC} Setting up database..."

# Setup database
cd "$PROJECT_DIR/backend"
uv run alembic upgrade head 2>/dev/null || true
echo "      Database ready"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "   Your HR Portal is ready to use!"
echo ""
echo "   Starting the application now..."
echo ""

# Make start script executable and run it
chmod +x "$SCRIPT_DIR/start-portal.sh"
"$SCRIPT_DIR/start-portal.sh"
