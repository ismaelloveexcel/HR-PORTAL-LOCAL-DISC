"""Onboarding service for employee self-service."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.employee_profile import EmployeeProfile
from app.models.onboarding_token import OnboardingToken
from app.schemas.employee import (
    EmployeeProfileSubmit,
    OnboardingTokenCreate,
    OnboardingTokenResponse,
    OnboardingValidation,
    OnboardingWelcome,
)


async def generate_onboarding_token(
    session: AsyncSession,
    employee_id: str,
    created_by: str,
    expires_in_days: int = 7,
    base_url: str = ""
) -> OnboardingTokenResponse:
    """Generate a unique onboarding token for a new joiner."""
    
    # Find the employee
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise ValueError(f"Employee {employee_id} not found")
    
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    
    # Calculate expiry
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
    
    # Create the token record
    onboarding_token = OnboardingToken(
        employee_id=employee.id,
        token=token,
        expires_at=expires_at,
        created_by=created_by,
    )
    
    session.add(onboarding_token)
    await session.commit()
    await session.refresh(onboarding_token)
    
    # Build the onboarding URL
    onboarding_url = f"{base_url}/onboarding/{token}"
    
    return OnboardingTokenResponse(
        token=token,
        employee_id=employee.employee_id,
        employee_name=employee.name,
        expires_at=expires_at,
        onboarding_url=onboarding_url,
        is_used=False,
    )


async def validate_onboarding_token(
    session: AsyncSession,
    token: str,
) -> OnboardingValidation:
    """Validate an onboarding token and return employee info if valid."""
    
    result = await session.execute(
        select(OnboardingToken).where(OnboardingToken.token == token)
    )
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        return OnboardingValidation(
            valid=False,
            message="Invalid token"
        )
    
    if token_record.is_used:
        return OnboardingValidation(
            valid=False,
            message="This onboarding link has already been used"
        )
    
    # Check expiry
    now = datetime.now(timezone.utc)
    if token_record.expires_at.tzinfo is None:
        token_expires = token_record.expires_at.replace(tzinfo=timezone.utc)
    else:
        token_expires = token_record.expires_at
        
    if now > token_expires:
        return OnboardingValidation(
            valid=False,
            message="This onboarding link has expired. Please contact HR for a new link."
        )
    
    # Update access count
    token_record.access_count += 1
    token_record.last_accessed_at = now
    await session.commit()
    
    # Get employee info
    result = await session.execute(
        select(Employee).where(Employee.id == token_record.employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        return OnboardingValidation(
            valid=False,
            message="Employee record not found"
        )
    
    return OnboardingValidation(
        valid=True,
        employee_id=employee.employee_id,
        employee_name=employee.name,
        message="Token is valid"
    )


async def get_onboarding_welcome(
    session: AsyncSession,
    token: str,
) -> Optional[OnboardingWelcome]:
    """Get welcome info for onboarding page."""
    
    result = await session.execute(
        select(OnboardingToken).where(OnboardingToken.token == token)
    )
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        return None
    
    result = await session.execute(
        select(Employee).where(Employee.id == token_record.employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        return None
    
    return OnboardingWelcome(
        employee_id=employee.employee_id,
        name=employee.name,
        email=employee.email,
        department=employee.department,
        job_title=employee.job_title,
        joining_date=employee.joining_date,
        line_manager_name=employee.line_manager_name,
        location=employee.location,
    )


async def submit_onboarding_profile(
    session: AsyncSession,
    token: str,
    profile_data: EmployeeProfileSubmit,
) -> dict:
    """Submit employee profile data via onboarding token.
    
    Security: Uses atomic check-and-mark to prevent race conditions
    and duplicate submissions.
    """
    
    # Get token record with FOR UPDATE to lock the row
    result = await session.execute(
        select(OnboardingToken).where(OnboardingToken.token == token).with_for_update()
    )
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        raise ValueError("Invalid token")
    
    # Check if already used (atomic check within transaction)
    if token_record.is_used:
        raise ValueError("This onboarding link has already been used")
    
    # Check expiry
    now = datetime.now(timezone.utc)
    if token_record.expires_at.tzinfo is None:
        token_expires = token_record.expires_at.replace(tzinfo=timezone.utc)
    else:
        token_expires = token_record.expires_at
        
    if now > token_expires:
        raise ValueError("This onboarding link has expired. Please contact HR for a new link.")
    
    # IMMEDIATELY mark token as used to prevent race conditions
    token_record.is_used = True
    token_record.used_at = now
    
    # Get employee record
    result = await session.execute(
        select(Employee).where(Employee.id == token_record.employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise ValueError("Employee record not found")
    
    # Get or create profile
    result = await session.execute(
        select(EmployeeProfile).where(EmployeeProfile.employee_id == token_record.employee_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = EmployeeProfile(employee_id=token_record.employee_id)
        session.add(profile)
    
    # Sanitize and update profile fields
    profile_dict = profile_data.model_dump(exclude_unset=True)
    
    # Basic sanitization - strip whitespace from text fields
    for field, value in profile_dict.items():
        if isinstance(value, str):
            value = value.strip()
            # Limit field length to prevent overflow
            if len(value) > 500:
                value = value[:500]
        setattr(profile, field, value)
    
    profile.submitted_at = now
    
    # Update employee profile status
    employee.profile_status = "pending_review"
    
    await session.commit()
    
    return {
        "success": True,
        "message": "Profile submitted successfully. HR will review your information.",
        "employee_id": employee.employee_id,
    }


async def get_pending_profiles(
    session: AsyncSession,
) -> list[dict]:
    """Get list of profiles pending HR review."""
    
    result = await session.execute(
        select(Employee).where(Employee.profile_status == "pending_review")
    )
    employees = result.scalars().all()
    
    pending = []
    for emp in employees:
        result = await session.execute(
            select(EmployeeProfile).where(EmployeeProfile.employee_id == emp.id)
        )
        profile = result.scalar_one_or_none()
        
        pending.append({
            "employee_id": emp.employee_id,
            "name": emp.name,
            "department": emp.department,
            "job_title": emp.job_title,
            "submitted_at": profile.submitted_at if profile else None,
            "profile": profile,
        })
    
    return pending


async def approve_profile(
    session: AsyncSession,
    employee_id: str,
    reviewer_id: str,
) -> dict:
    """Approve an employee's submitted profile."""
    
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise ValueError(f"Employee {employee_id} not found")
    
    if employee.profile_status != "pending_review":
        raise ValueError(f"Profile is not pending review (status: {employee.profile_status})")
    
    # Update profile
    result = await session.execute(
        select(EmployeeProfile).where(EmployeeProfile.employee_id == employee.id)
    )
    profile = result.scalar_one_or_none()
    
    if profile:
        profile.reviewed_at = datetime.now(timezone.utc)
        profile.reviewed_by = reviewer_id
    
    # Update employee status
    employee.profile_status = "complete"
    
    await session.commit()
    
    return {
        "success": True,
        "message": f"Profile for {employee.name} approved",
        "employee_id": employee_id,
    }


async def list_onboarding_tokens(
    session: AsyncSession,
) -> list[dict]:
    """List all onboarding tokens with their status."""
    
    result = await session.execute(
        select(OnboardingToken, Employee)
        .join(Employee, OnboardingToken.employee_id == Employee.id)
        .order_by(OnboardingToken.created_at.desc())
    )
    rows = result.all()
    
    tokens = []
    for token_record, employee in rows:
        now = datetime.now(timezone.utc)
        if token_record.expires_at.tzinfo is None:
            token_expires = token_record.expires_at.replace(tzinfo=timezone.utc)
        else:
            token_expires = token_record.expires_at
        
        is_expired = now > token_expires
        
        tokens.append({
            "token": token_record.token,
            "employee_id": employee.employee_id,
            "employee_name": employee.name,
            "created_at": token_record.created_at,
            "expires_at": token_record.expires_at,
            "is_used": token_record.is_used,
            "is_expired": is_expired,
            "access_count": token_record.access_count,
        })
    
    return tokens
