"""Geofence schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GeofenceCreate(BaseModel):
    """Create a new geofence."""
    name: str = Field(..., description="Location name (must match WORK_LOCATIONS)")
    description: Optional[str] = Field(default=None, description="Location description")
    latitude: Decimal = Field(..., description="Center latitude")
    longitude: Decimal = Field(..., description="Center longitude")
    radius_meters: int = Field(default=100, description="Radius in meters")
    address: Optional[str] = Field(default=None, description="Address for display")
    validation_required: bool = Field(default=False, description="Is geofence validation required?")


class GeofenceUpdate(BaseModel):
    """Update a geofence."""
    description: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    radius_meters: Optional[int] = None
    address: Optional[str] = None
    validation_required: Optional[bool] = None
    is_active: Optional[bool] = None


class GeofenceResponse(BaseModel):
    """Geofence response."""
    id: int
    name: str
    description: Optional[str] = None
    latitude: Decimal
    longitude: Decimal
    radius_meters: int
    address: Optional[str] = None
    is_active: bool
    validation_required: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GeofenceValidationRequest(BaseModel):
    """Request to validate GPS coordinates against geofences."""
    latitude: Decimal = Field(..., description="User's latitude")
    longitude: Decimal = Field(..., description="User's longitude")
    work_location: Optional[str] = Field(default=None, description="Expected work location")


class GeofenceValidationResponse(BaseModel):
    """Response from geofence validation."""
    is_valid: bool
    work_location: Optional[str] = None
    matched_geofence: Optional[str] = None
    distance_meters: Optional[float] = None
    within_radius: bool = False
    validation_required: bool = False
    message: str


class NearbyGeofence(BaseModel):
    """Nearby geofence information."""
    name: str
    distance_meters: float
    within_radius: bool
    latitude: Decimal
    longitude: Decimal
    radius_meters: int
