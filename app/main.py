"""
Root-level FastAPI application entry point for Azure App Service.

Azure's Oryx build system expects app/main.py with `app = FastAPI()`.
This module re-exports the FastAPI app from the backend package.
"""
import sys
from pathlib import Path

# Add backend to Python path so we can import from backend.app
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the FastAPI app from the backend
from app.main import app

# Expose the app for gunicorn: gunicorn app.main:app
__all__ = ["app"]
