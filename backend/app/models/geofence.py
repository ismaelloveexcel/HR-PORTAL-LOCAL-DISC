"""Geofence model for location-based attendance validation.

This module provides:
- Define office locations with GPS coordinates and radius
- Validate clock-in/out locations against defined geofences
- Flag attendance records outside allowed locations
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
import math

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.renewal import Base


class Geofence(Base):
    """Geofence definition for office/work locations.
    
    Defines a circular area around a center point.
    Used to validate if employee clock-in/out is within allowed location.
    """
    __tablename__ = "geofences"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Location identification (maps to WORK_LOCATIONS)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # GPS center point
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    
    # Radius in meters
    radius_meters: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    
    # Address for display
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Is this geofence active?
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Is geofence validation required for this location?
    # If true, clock-in outside radius will be flagged
    validation_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the distance between two GPS coordinates in meters.
    
    Uses the Haversine formula for great-circle distance.
    
    Args:
        lat1, lon1: First point coordinates (decimal degrees)
        lat2, lon2: Second point coordinates (decimal degrees)
        
    Returns:
        Distance in meters
    """
    R = 6371000  # Earth's radius in meters
    
    # Convert to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def is_within_geofence(
    user_lat: float, 
    user_lon: float, 
    geofence_lat: float, 
    geofence_lon: float, 
    radius_meters: int
) -> tuple[bool, float]:
    """Check if a point is within a geofence.
    
    Args:
        user_lat, user_lon: User's GPS coordinates
        geofence_lat, geofence_lon: Geofence center coordinates
        radius_meters: Geofence radius in meters
        
    Returns:
        Tuple of (is_within: bool, distance_meters: float)
    """
    distance = haversine_distance(user_lat, user_lon, geofence_lat, geofence_lon)
    is_within = distance <= radius_meters
    return is_within, distance


# Default geofences for known office locations
DEFAULT_GEOFENCES = [
    {
        "name": "Head Office",
        "description": "Baynunah Head Office - Abu Dhabi",
        "latitude": Decimal("24.4539"),
        "longitude": Decimal("54.3773"),
        "radius_meters": 200,
        "address": "Abu Dhabi, UAE",
        "is_active": True,
        "validation_required": True
    },
    {
        "name": "KEZAD",
        "description": "Khalifa Industrial Zone Abu Dhabi",
        "latitude": Decimal("24.6400"),
        "longitude": Decimal("54.6350"),
        "radius_meters": 500,
        "address": "KIZAD, Abu Dhabi, UAE",
        "is_active": True,
        "validation_required": True
    },
    {
        "name": "Safario",
        "description": "Safario Manufacturing Facility",
        "latitude": Decimal("24.3500"),
        "longitude": Decimal("54.5000"),
        "radius_meters": 300,
        "address": "Abu Dhabi, UAE",
        "is_active": True,
        "validation_required": True
    }
    # Note: Sites, Meeting, Event, WFH don't have fixed geofences
]
