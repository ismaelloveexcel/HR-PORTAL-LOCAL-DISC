"""Public holidays model for UAE and company-specific holidays.

This module integrates with the Attendance module to:
- Mark attendance records as "holiday" work type
- Apply 150% overtime rate for holiday work
- Auto-calculate if an employee worked on a public holiday
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.renewal import Base


# UAE Official Public Holidays
# These are mandated by Federal Decree
UAE_PUBLIC_HOLIDAYS = [
    "new_year",             # January 1 - New Year's Day
    "eid_al_fitr",          # Eid Al Fitr (3-4 days, varies)
    "arafat_day",           # Arafat Day (1 day)
    "eid_al_adha",          # Eid Al Adha (3-4 days, varies)
    "hijri_new_year",       # Islamic New Year (1 day)
    "prophet_birthday",     # Prophet's Birthday (1 day)
    "commemoration_day",    # November 30 - Commemoration Day
    "national_day"          # December 2-3 - UAE National Day
]


class PublicHoliday(Base):
    """Public holiday definition.
    
    Supports:
    - UAE official holidays (mandatory)
    - Company-specific holidays (optional)
    - Custom dates for Islamic holidays (calculated by HR)
    """
    __tablename__ = "public_holidays"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Holiday identification
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_arabic: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Date range (some holidays span multiple days)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Year for easy filtering
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Holiday type
    holiday_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "uae_official", "company", "optional"
    
    # Is this a paid holiday?
    is_paid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Description/notes
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Is active (can be disabled for specific years)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Created by (HR user)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


# UAE 2026 Public Holidays (Official)
# Based on UAE Federal Government announcements and Islamic calendar estimations
# Total: 8 holidays (14 days including multi-day holidays like Eid and National Day)
UAE_HOLIDAYS_2026 = [
    {
        "name": "New Year's Day",
        "name_arabic": "رأس السنة الميلادية",
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 1, 1),
        "year": 2026,
        "holiday_type": "uae_official",
        "is_paid": True,
        "description": "New Year's Day - January 1"
    },
    {
        "name": "Eid Al Fitr",
        "name_arabic": "عيد الفطر",
        "start_date": date(2026, 3, 20),
        "end_date": date(2026, 3, 23),
        "year": 2026,
        "holiday_type": "uae_official",
        "is_paid": True,
        "description": "Eid Al Fitr - 4 days (approximate, subject to moon sighting)"
    },
    {
        "name": "Arafat Day",
        "name_arabic": "يوم عرفة",
        "start_date": date(2026, 5, 26),
        "end_date": date(2026, 5, 26),
        "year": 2026,
        "holiday_type": "uae_official",
        "is_paid": True,
        "description": "Arafat Day - Day before Eid Al Adha (approximate)"
    },
    {
        "name": "Eid Al Adha",
        "name_arabic": "عيد الأضحى",
        "start_date": date(2026, 5, 27),
        "end_date": date(2026, 5, 29),
        "year": 2026,
        "holiday_type": "uae_official",
        "is_paid": True,
        "description": "Eid Al Adha - 3 days (approximate, subject to moon sighting)"
    },
    {
        "name": "Islamic New Year",
        "name_arabic": "رأس السنة الهجرية",
        "start_date": date(2026, 6, 16),
        "end_date": date(2026, 6, 16),
        "year": 2026,
        "holiday_type": "uae_official",
        "is_paid": True,
        "description": "Hijri New Year 1448 (approximate)"
    },
    {
        "name": "Prophet's Birthday",
        "name_arabic": "المولد النبوي الشريف",
        "start_date": date(2026, 8, 25),
        "end_date": date(2026, 8, 25),
        "year": 2026,
        "holiday_type": "uae_official",
        "is_paid": True,
        "description": "Mawlid Al Nabi - Prophet Muhammad's Birthday (approximate)"
    },
    {
        "name": "Commemoration Day",
        "name_arabic": "يوم الشهيد",
        "start_date": date(2026, 11, 30),
        "end_date": date(2026, 11, 30),
        "year": 2026,
        "holiday_type": "uae_official",
        "is_paid": True,
        "description": "Martyrs' Day - November 30 (formerly Nov 30, moved to Dec 1 if on weekend)"
    },
    {
        "name": "UAE National Day",
        "name_arabic": "اليوم الوطني لدولة الإمارات",
        "start_date": date(2026, 12, 2),
        "end_date": date(2026, 12, 3),
        "year": 2026,
        "holiday_type": "uae_official",
        "is_paid": True,
        "description": "UAE National Day - December 2-3 (48th & 49th Anniversary)"
    }
]


# Default UAE Public Holidays for a year (dates to be updated by HR)
def get_default_uae_holidays(year: int) -> list:
    """Get default UAE public holiday templates for a year.
    
    Note: Islamic holidays are approximate and should be confirmed by HR
    based on moon sighting announcements from the UAE Government.
    
    For 2026, use UAE_HOLIDAYS_2026 constant which contains 8 official holidays
    (14 total days including multi-day holidays).
    
    Returns:
        list: List of holiday dictionaries with dates and metadata
    """
    if year == 2026:
        return UAE_HOLIDAYS_2026
    
    # Fallback for other years - basic holidays only
    return [
        {
            "name": "New Year's Day",
            "name_arabic": "رأس السنة الميلادية",
            "start_date": date(year, 1, 1),
            "end_date": date(year, 1, 1),
            "year": year,
            "holiday_type": "uae_official",
            "is_paid": True,
            "description": "New Year's Day - January 1"
        },
        {
            "name": "Commemoration Day",
            "name_arabic": "يوم الشهيد",
            "start_date": date(year, 11, 30),
            "end_date": date(year, 11, 30),
            "year": year,
            "holiday_type": "uae_official",
            "is_paid": True,
            "description": "Martyr's Day - November 30"
        },
        {
            "name": "UAE National Day",
            "name_arabic": "اليوم الوطني لدولة الإمارات",
            "start_date": date(year, 12, 2),
            "end_date": date(year, 12, 3),
            "year": year,
            "holiday_type": "uae_official",
            "is_paid": True,
            "description": "UAE National Day - December 2-3"
        }
        # Islamic holidays (Eid Al Fitr, Eid Al Adha, etc.) 
        # should be added by HR when dates are announced
    ]
