"""Public holiday management router."""
from datetime import date

from fastapi import APIRouter, Depends, Header, HTTPException, status
import jwt
from jwt.exceptions import PyJWTError
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database import get_session
from app.models.employee import Employee
from app.models.public_holiday import PublicHoliday, get_default_uae_holidays
from app.schemas.public_holiday import (
    PublicHolidayCreate, PublicHolidayUpdate, PublicHolidayResponse,
    HolidayCalendar, IsHolidayResponse
)

router = APIRouter(prefix="/holidays", tags=["Public Holidays"])


async def get_current_employee(
    authorization: str = Header(...),
    session: AsyncSession = Depends(get_session)
) -> Employee:
    """Extract and validate employee from JWT token."""
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
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        result = await session.execute(
            select(Employee).where(Employee.id == int(employee_id))
        )
        employee = result.scalar_one_or_none()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")


@router.get("/year/{year}", response_model=HolidayCalendar)
async def get_holidays_by_year(
    year: int,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Get all public holidays for a year."""
    result = await session.execute(
        select(PublicHoliday).where(
            and_(
                PublicHoliday.year == year,
                PublicHoliday.is_active == True
            )
        ).order_by(PublicHoliday.start_date)
    )
    holidays = result.scalars().all()
    
    # Calculate total days off
    total_days = sum((h.end_date - h.start_date).days + 1 for h in holidays)
    
    return HolidayCalendar(
        year=year,
        total_holidays=len(holidays),
        total_days_off=total_days,
        holidays=[
            PublicHolidayResponse(
                id=h.id,
                name=h.name,
                name_arabic=h.name_arabic,
                start_date=h.start_date,
                end_date=h.end_date,
                year=h.year,
                holiday_type=h.holiday_type,
                is_paid=h.is_paid,
                description=h.description,
                is_active=h.is_active,
                created_at=h.created_at
            )
            for h in holidays
        ]
    )


@router.get("/check/{check_date}", response_model=IsHolidayResponse)
async def check_if_holiday(
    check_date: date,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Check if a specific date is a public holiday."""
    result = await session.execute(
        select(PublicHoliday).where(
            and_(
                PublicHoliday.is_active == True,
                PublicHoliday.start_date <= check_date,
                PublicHoliday.end_date >= check_date
            )
        )
    )
    holiday = result.scalar_one_or_none()
    
    if holiday:
        return IsHolidayResponse(
            date=check_date,
            is_holiday=True,
            holiday=PublicHolidayResponse(
                id=holiday.id,
                name=holiday.name,
                name_arabic=holiday.name_arabic,
                start_date=holiday.start_date,
                end_date=holiday.end_date,
                year=holiday.year,
                holiday_type=holiday.holiday_type,
                is_paid=holiday.is_paid,
                description=holiday.description,
                is_active=holiday.is_active,
                created_at=holiday.created_at
            )
        )
    
    return IsHolidayResponse(
        date=check_date,
        is_holiday=False,
        holiday=None
    )


@router.post("/", response_model=PublicHolidayResponse)
async def create_holiday(
    holiday: PublicHolidayCreate,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Create a new public holiday (HR/Admin only)."""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only HR/Admin can create holidays")
    
    new_holiday = PublicHoliday(
        name=holiday.name,
        name_arabic=holiday.name_arabic,
        start_date=holiday.start_date,
        end_date=holiday.end_date,
        year=holiday.year,
        holiday_type=holiday.holiday_type,
        is_paid=holiday.is_paid,
        description=holiday.description,
        created_by=current_user.id
    )
    
    session.add(new_holiday)
    await session.commit()
    await session.refresh(new_holiday)
    
    return PublicHolidayResponse(
        id=new_holiday.id,
        name=new_holiday.name,
        name_arabic=new_holiday.name_arabic,
        start_date=new_holiday.start_date,
        end_date=new_holiday.end_date,
        year=new_holiday.year,
        holiday_type=new_holiday.holiday_type,
        is_paid=new_holiday.is_paid,
        description=new_holiday.description,
        is_active=new_holiday.is_active,
        created_at=new_holiday.created_at
    )


@router.put("/{holiday_id}", response_model=PublicHolidayResponse)
async def update_holiday(
    holiday_id: int,
    update: PublicHolidayUpdate,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Update a public holiday (HR/Admin only)."""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only HR/Admin can update holidays")
    
    result = await session.execute(
        select(PublicHoliday).where(PublicHoliday.id == holiday_id)
    )
    holiday = result.scalar_one_or_none()
    
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    
    # Update fields
    if update.name is not None:
        holiday.name = update.name
    if update.name_arabic is not None:
        holiday.name_arabic = update.name_arabic
    if update.start_date is not None:
        holiday.start_date = update.start_date
    if update.end_date is not None:
        holiday.end_date = update.end_date
    if update.holiday_type is not None:
        holiday.holiday_type = update.holiday_type
    if update.is_paid is not None:
        holiday.is_paid = update.is_paid
    if update.description is not None:
        holiday.description = update.description
    if update.is_active is not None:
        holiday.is_active = update.is_active
    
    await session.commit()
    await session.refresh(holiday)
    
    return PublicHolidayResponse(
        id=holiday.id,
        name=holiday.name,
        name_arabic=holiday.name_arabic,
        start_date=holiday.start_date,
        end_date=holiday.end_date,
        year=holiday.year,
        holiday_type=holiday.holiday_type,
        is_paid=holiday.is_paid,
        description=holiday.description,
        is_active=holiday.is_active,
        created_at=holiday.created_at
    )


@router.post("/init/{year}")
async def initialize_default_holidays(
    year: int,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Initialize default UAE holidays for a year (HR/Admin only).
    
    Creates templates for standard UAE holidays. Islamic holidays
    need to have their dates updated when announced.
    """
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only HR/Admin can initialize holidays")
    
    # Check if holidays already exist for this year
    existing = await session.execute(
        select(PublicHoliday).where(PublicHoliday.year == year).limit(1)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Holidays already exist for year {year}")
    
    defaults = get_default_uae_holidays(year)
    created = []
    
    for h in defaults:
        holiday = PublicHoliday(
            name=h["name"],
            name_arabic=h["name_arabic"],
            start_date=h["start_date"],
            end_date=h["end_date"],
            year=h["year"],
            holiday_type=h["holiday_type"],
            is_paid=h["is_paid"],
            description=h["description"],
            created_by=current_user.id
        )
        session.add(holiday)
        created.append(h["name"])
    
    await session.commit()
    
    return {
        "status": "success",
        "year": year,
        "created_count": len(created),
        "holidays": created,
        "note": "Islamic holidays (Eid Al Fitr, Eid Al Adha, etc.) need to be added manually when dates are announced"
    }
