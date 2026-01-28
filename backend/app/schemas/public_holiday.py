"""Public holiday schemas."""
from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class PublicHolidayCreate(BaseModel):
    """Create a new public holiday."""
    name: str = Field(..., description="Holiday name in English")
    name_arabic: Optional[str] = Field(default=None, description="Holiday name in Arabic")
    start_date: date = Field(..., description="Holiday start date")
    end_date: date = Field(..., description="Holiday end date")
    year: int = Field(..., description="Year")
    holiday_type: str = Field(default="uae_official", description="uae_official, company, or optional")
    is_paid: bool = Field(default=True, description="Is this a paid holiday?")
    description: Optional[str] = Field(default=None, description="Holiday description")


class PublicHolidayUpdate(BaseModel):
    """Update a public holiday."""
    name: Optional[str] = None
    name_arabic: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    holiday_type: Optional[str] = None
    is_paid: Optional[bool] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PublicHolidayResponse(BaseModel):
    """Public holiday response."""
    id: int
    name: str
    name_arabic: Optional[str] = None
    start_date: date
    end_date: date
    year: int
    holiday_type: str
    is_paid: bool
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class HolidayCalendar(BaseModel):
    """Yearly holiday calendar."""
    year: int
    total_holidays: int
    total_days_off: int
    holidays: List[PublicHolidayResponse] = []


class IsHolidayResponse(BaseModel):
    """Check if a date is a holiday."""
    date: date
    is_holiday: bool
    holiday: Optional[PublicHolidayResponse] = None
