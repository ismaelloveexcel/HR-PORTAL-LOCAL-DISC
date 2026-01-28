from typing import Any
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, status
import jwt
from jwt.exceptions import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import hashlib

from app.core.config import get_settings
from app.database import get_session
from app.schemas.employee import (
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
)
from app.services.employees import employee_service, create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)


def _hash_employee_id(employee_id: str) -> str:
    """Creates a SHA-256 hash for logging without exposing sensitive employee IDs."""
    return hashlib.sha256(employee_id.encode("utf-8")).hexdigest()


def _log_login_error(employee_id: str, error_type: str, label: str) -> None:
    employee_id_hash = _hash_employee_id(employee_id)
    logger.error(f"{label} for employee_id_hash={employee_id_hash}: {error_type}")


async def get_current_employee_id(authorization: str = Header(...)) -> str:
    """Extract employee ID from JWT token."""
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header",
            )
        settings = get_settings()
        payload = jwt.decode(token, settings.auth_secret_key, algorithms=["HS256"])
        employee_id = payload.get("sub")
        if not employee_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        return employee_id
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login with Employee ID and password",
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Authenticate with Employee ID and password.
    
    - **First-time login**: Use DOB in DDMMYYYY format as password
    - **Subsequent logins**: Use your custom password
    
    If `requires_password_change` is true, you must change your password.
    """
    try:
        return await employee_service.login(session, request)
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        _log_login_error(request.employee_id, type(e).__name__, "Login database error")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login unavailable. Database connection failed.",
        )
    except Exception as e:
        # Log error type and a hashed employee_id for debugging (avoid logging sensitive data)
        error_type = type(e).__name__
        _log_login_error(request.employee_id, error_type, "Login error")
        # Note: Traceback intentionally not logged to avoid potential sensitive data exposure
        
        # In development, show error type only (not the full message)
        settings = get_settings()
        if settings.app_env == "development":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login error: {error_type}",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during login. Please check server logs or contact support.",
            )


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
)
async def change_password(
    request: PasswordChangeRequest,
    employee_id: str = Depends(get_current_employee_id),
    session: AsyncSession = Depends(get_session),
):
    """
    Change your password. Requires authentication.
    
    Password requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    success = await employee_service.change_password(session, employee_id, request)
    return {"success": success, "message": "Password changed successfully"}
