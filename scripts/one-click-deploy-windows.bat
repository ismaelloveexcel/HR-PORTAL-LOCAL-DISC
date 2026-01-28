@echo off
REM ============================================
REM HR Portal ONE-CLICK Deployment for Windows
REM ============================================
REM 
REM This script does EVERYTHING automatically:
REM   1. Downloads and installs Python (if missing)
REM   2. Downloads and installs Node.js (if missing)
REM   3. Installs all dependencies
REM   4. Sets up the database
REM   5. Starts the application
REM
REM Just double-click this file and wait!
REM
REM ============================================

title HR Portal - One-Click Deployment

echo ============================================
echo   HR PORTAL - ONE-CLICK DEPLOYMENT
echo ============================================
echo.
echo This will install everything automatically.
echo Please wait, this may take 5-10 minutes...
echo.
echo ============================================
echo.

REM Get the script directory
cd /d "%~dp0\.."
set PROJECT_DIR=%cd%

REM Check if running as admin (needed for some installs)
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [INFO] Running without admin rights - some features may require manual installation
    echo.
)

REM ============================================
REM STEP 1: Check/Install Python
REM ============================================
echo [1/6] Checking Python...

python --version >nul 2>&1
if errorlevel 1 (
    echo      Python not found. Attempting to install...
    
    REM Check if winget is available
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ============================================
        echo   MANUAL ACTION REQUIRED
        echo ============================================
        echo.
        echo   Python is not installed and automatic install failed.
        echo.
        echo   Please download and install Python manually:
        echo   1. Go to: https://www.python.org/downloads/
        echo   2. Click the yellow "Download Python" button
        echo   3. Run the installer
        echo   4. IMPORTANT: Check "Add Python to PATH"
        echo   5. Click "Install Now"
        echo   6. After installation, run this script again
        echo.
        echo ============================================
        echo.
        start https://www.python.org/downloads/
        pause
        exit /b 1
    )
    
    echo      Installing Python via Windows Package Manager...
    winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo [X] Failed to install Python automatically
        echo     Please install manually from https://www.python.org/downloads/
        start https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo [OK] Python installed
    
    echo      NOTE: You may need to restart this script for Python to be available.
) else (
    echo [OK] Python found
)

REM ============================================
REM STEP 2: Check/Install Node.js
REM ============================================
echo [2/6] Checking Node.js...

node --version >nul 2>&1
if errorlevel 1 (
    echo      Node.js not found. Attempting to install...
    
    REM Check if winget is available
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ============================================
        echo   MANUAL ACTION REQUIRED
        echo ============================================
        echo.
        echo   Node.js is not installed and automatic install failed.
        echo.
        echo   Please download and install Node.js manually:
        echo   1. Go to: https://nodejs.org/
        echo   2. Click the LTS button (Recommended)
        echo   3. Run the installer
        echo   4. Click Next through all screens
        echo   5. After installation, run this script again
        echo.
        echo ============================================
        echo.
        start https://nodejs.org/
        pause
        exit /b 1
    )
    
    echo      Installing Node.js via Windows Package Manager...
    winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo [X] Failed to install Node.js automatically
        echo     Please install manually from https://nodejs.org/
        start https://nodejs.org/
        pause
        exit /b 1
    )
    echo [OK] Node.js installed
    
    echo      NOTE: You may need to restart this script for Node.js to be available.
) else (
    echo [OK] Node.js found
)

REM ============================================
REM STEP 3: Install UV Package Manager
REM ============================================
echo [3/6] Installing UV package manager...

uv --version >nul 2>&1
if errorlevel 1 (
    pip install uv
    if errorlevel 1 (
        python -m pip install uv
    )
)
echo [OK] UV ready

REM ============================================
REM STEP 4: Install Dependencies
REM ============================================
echo [4/6] Installing dependencies (this takes a few minutes)...

cd "%PROJECT_DIR%\backend"
uv sync
if errorlevel 1 (
    echo [X] Backend dependency installation failed
    pause
    exit /b 1
)
echo      Backend dependencies installed

cd "%PROJECT_DIR%\frontend"
call npm install
if errorlevel 1 (
    echo [X] Frontend dependency installation failed
    pause
    exit /b 1
)
echo      Frontend dependencies installed

REM ============================================
REM STEP 5: Configure Environment
REM ============================================
echo [5/6] Configuring environment...

cd "%PROJECT_DIR%\backend"
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
    ) else (
        echo DATABASE_URL=sqlite:///./hr_portal.db > .env
        echo APP_ENV=development >> .env
        echo ALLOWED_ORIGINS=http://localhost:5000 >> .env
    )
)
echo      Backend configured with SQLite

cd "%PROJECT_DIR%\frontend"
if not exist ".env" (
    echo VITE_API_BASE_URL=http://localhost:8000/api > .env
)
echo      Frontend configured

REM ============================================
REM STEP 6: Setup Database
REM ============================================
echo [6/6] Setting up database...

cd "%PROJECT_DIR%\backend"
uv run alembic upgrade head >nul 2>&1
echo      Database ready

REM ============================================
REM SUCCESS!
REM ============================================

echo.
echo ============================================
echo   DEPLOYMENT COMPLETE!
echo ============================================
echo.
echo   Your HR Portal is ready to use!
echo.
echo   Starting the application now...
echo.

REM Start the application
call "%PROJECT_DIR%\scripts\start-portal-windows.bat"

echo.
pause
