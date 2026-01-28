"""Onboarding API endpoints for employee self-service."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.core.security import require_role
from app.schemas.employee import (
    EmployeeProfileSubmit,
    EmployeeProfileResponse,
    OnboardingTokenCreate,
    OnboardingTokenResponse,
    OnboardingValidation,
    OnboardingWelcome,
)
from app.services import onboarding as onboarding_service

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


# Public endpoints (no auth required - token-based access)

@router.get(
    "/validate/{token}",
    response_model=OnboardingValidation,
    summary="Validate onboarding token",
)
async def validate_token(
    token: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Validate an onboarding token.
    
    This is a public endpoint - no authentication required.
    The token itself provides access control.
    """
    return await onboarding_service.validate_onboarding_token(session, token)


@router.get(
    "/welcome/{token}",
    response_model=OnboardingWelcome,
    summary="Get welcome info for onboarding",
)
async def get_welcome(
    token: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get employee welcome information for the onboarding page.
    
    Returns basic info like name, department, job title that
    the new joiner can see when completing their profile.
    """
    # First validate the token
    validation = await onboarding_service.validate_onboarding_token(session, token)
    if not validation.valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation.message
        )
    
    welcome = await onboarding_service.get_onboarding_welcome(session, token)
    if not welcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee information not found"
        )
    
    return welcome


@router.post(
    "/submit/{token}",
    summary="Submit onboarding profile",
)
async def submit_profile(
    token: str,
    profile: EmployeeProfileSubmit,
    session: AsyncSession = Depends(get_session),
):
    """
    Submit employee profile data.
    
    New joiners use this endpoint to complete their profile.
    After submission, the profile goes to HR for review.
    """
    try:
        result = await onboarding_service.submit_onboarding_profile(
            session, token, profile
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Protected endpoints (HR/Admin only)

@router.post(
    "/invite",
    response_model=OnboardingTokenResponse,
    summary="Generate onboarding invite link",
)
async def create_invite(
    data: OnboardingTokenCreate,
    request: Request,
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Generate an onboarding invite link for a new joiner.
    
    **Admin and HR only.**
    
    The link can be shared with the employee via email or messaging.
    They can use it to complete their profile without logging in.
    """
    # Get base URL from request
    base_url = str(request.base_url).rstrip("/")
    
    try:
        result = await onboarding_service.generate_onboarding_token(
            session=session,
            employee_id=data.employee_id,
            created_by=role,
            expires_in_days=data.expires_in_days,
            base_url=base_url,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/pending",
    summary="List profiles pending review",
)
async def list_pending(
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Get list of employee profiles pending HR review.
    
    **Admin and HR only.**
    """
    return await onboarding_service.get_pending_profiles(session)


@router.post(
    "/approve/{employee_id}",
    summary="Approve employee profile",
)
async def approve(
    employee_id: str,
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Approve an employee's submitted profile.
    
    **Admin and HR only.**
    """
    try:
        return await onboarding_service.approve_profile(
            session, employee_id, role
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/tokens",
    summary="List all onboarding tokens",
)
async def list_tokens(
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    List all onboarding tokens with their status.
    
    **Admin and HR only.**
    
    Shows which tokens are used, expired, or still active.
    """
    return await onboarding_service.list_onboarding_tokens(session)
