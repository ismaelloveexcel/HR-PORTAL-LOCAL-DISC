"""Geofence management router."""
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
import jwt
from jwt.exceptions import PyJWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database import get_session
from app.models.employee import Employee
from app.models.geofence import Geofence, DEFAULT_GEOFENCES, is_within_geofence
from app.schemas.geofence import (
    GeofenceCreate, GeofenceUpdate, GeofenceResponse,
    GeofenceValidationRequest, GeofenceValidationResponse, NearbyGeofence
)
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/geofences", tags=["Geofences"])


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


@router.get("/", response_model=List[GeofenceResponse])
async def list_geofences(
    active_only: bool = Query(True, description="Only show active geofences"),
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """List all geofences."""
    query = select(Geofence)
    if active_only:
        query = query.where(Geofence.is_active == True)
    
    result = await session.execute(query.order_by(Geofence.name))
    geofences = result.scalars().all()
    
    return [
        GeofenceResponse(
            id=g.id,
            name=g.name,
            description=g.description,
            latitude=g.latitude,
            longitude=g.longitude,
            radius_meters=g.radius_meters,
            address=g.address,
            is_active=g.is_active,
            validation_required=g.validation_required,
            created_at=g.created_at
        )
        for g in geofences
    ]


@router.get("/{geofence_id}", response_model=GeofenceResponse)
async def get_geofence(
    geofence_id: int,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Get a specific geofence."""
    result = await session.execute(
        select(Geofence).where(Geofence.id == geofence_id)
    )
    geofence = result.scalar_one_or_none()
    
    if not geofence:
        raise HTTPException(status_code=404, detail="Geofence not found")
    
    return GeofenceResponse(
        id=geofence.id,
        name=geofence.name,
        description=geofence.description,
        latitude=geofence.latitude,
        longitude=geofence.longitude,
        radius_meters=geofence.radius_meters,
        address=geofence.address,
        is_active=geofence.is_active,
        validation_required=geofence.validation_required,
        created_at=geofence.created_at
    )


@router.post("/", response_model=GeofenceResponse)
async def create_geofence(
    geofence: GeofenceCreate,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Create a new geofence (HR/Admin only)."""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only HR/Admin can create geofences")
    
    # Check for duplicate name
    existing = await session.execute(
        select(Geofence).where(Geofence.name == geofence.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Geofence with name '{geofence.name}' already exists")
    
    new_geofence = Geofence(
        name=geofence.name,
        description=geofence.description,
        latitude=geofence.latitude,
        longitude=geofence.longitude,
        radius_meters=geofence.radius_meters,
        address=geofence.address,
        validation_required=geofence.validation_required
    )
    
    session.add(new_geofence)
    await session.commit()
    await session.refresh(new_geofence)
    
    return GeofenceResponse(
        id=new_geofence.id,
        name=new_geofence.name,
        description=new_geofence.description,
        latitude=new_geofence.latitude,
        longitude=new_geofence.longitude,
        radius_meters=new_geofence.radius_meters,
        address=new_geofence.address,
        is_active=new_geofence.is_active,
        validation_required=new_geofence.validation_required,
        created_at=new_geofence.created_at
    )


@router.put("/{geofence_id}", response_model=GeofenceResponse)
async def update_geofence(
    geofence_id: int,
    update: GeofenceUpdate,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Update a geofence (HR/Admin only)."""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only HR/Admin can update geofences")
    
    result = await session.execute(
        select(Geofence).where(Geofence.id == geofence_id)
    )
    geofence = result.scalar_one_or_none()
    
    if not geofence:
        raise HTTPException(status_code=404, detail="Geofence not found")
    
    # Update fields
    if update.description is not None:
        geofence.description = update.description
    if update.latitude is not None:
        geofence.latitude = update.latitude
    if update.longitude is not None:
        geofence.longitude = update.longitude
    if update.radius_meters is not None:
        geofence.radius_meters = update.radius_meters
    if update.address is not None:
        geofence.address = update.address
    if update.validation_required is not None:
        geofence.validation_required = update.validation_required
    if update.is_active is not None:
        geofence.is_active = update.is_active
    
    await session.commit()
    await session.refresh(geofence)
    
    return GeofenceResponse(
        id=geofence.id,
        name=geofence.name,
        description=geofence.description,
        latitude=geofence.latitude,
        longitude=geofence.longitude,
        radius_meters=geofence.radius_meters,
        address=geofence.address,
        is_active=geofence.is_active,
        validation_required=geofence.validation_required,
        created_at=geofence.created_at
    )


@router.post("/validate", response_model=GeofenceValidationResponse)
async def validate_location(
    request: GeofenceValidationRequest,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Validate GPS coordinates against geofences.
    
    Used during clock-in/out to verify employee is at expected location.
    """
    service = AttendanceService(session)
    result = await service.validate_geofence(
        float(request.latitude),
        float(request.longitude),
        request.work_location
    )
    
    return GeofenceValidationResponse(
        is_valid=result["is_valid"],
        work_location=result.get("work_location"),
        matched_geofence=result.get("matched_geofence"),
        distance_meters=result.get("distance_meters"),
        within_radius=result.get("within_radius", False),
        validation_required=result.get("validation_required", False),
        message=result["message"]
    )


@router.get("/nearby", response_model=List[NearbyGeofence])
async def get_nearby_geofences(
    latitude: float = Query(..., description="Current latitude"),
    longitude: float = Query(..., description="Current longitude"),
    max_distance: int = Query(5000, description="Maximum distance in meters"),
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Get geofences near a location, sorted by distance."""
    result = await session.execute(
        select(Geofence).where(Geofence.is_active == True)
    )
    geofences = result.scalars().all()
    
    nearby = []
    for gf in geofences:
        is_within, distance = is_within_geofence(
            latitude, longitude,
            float(gf.latitude), float(gf.longitude),
            gf.radius_meters
        )
        
        if distance <= max_distance:
            nearby.append({
                "name": gf.name,
                "distance_meters": distance,
                "within_radius": is_within,
                "latitude": gf.latitude,
                "longitude": gf.longitude,
                "radius_meters": gf.radius_meters
            })
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_meters"])
    
    return [NearbyGeofence(**g) for g in nearby]


@router.post("/init")
async def initialize_default_geofences(
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Initialize default geofences for known office locations (HR/Admin only)."""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only HR/Admin can initialize geofences")
    
    created = []
    skipped = []
    
    for gf_data in DEFAULT_GEOFENCES:
        # Check if already exists
        existing = await session.execute(
            select(Geofence).where(Geofence.name == gf_data["name"])
        )
        if existing.scalar_one_or_none():
            skipped.append(gf_data["name"])
            continue
        
        geofence = Geofence(
            name=gf_data["name"],
            description=gf_data["description"],
            latitude=gf_data["latitude"],
            longitude=gf_data["longitude"],
            radius_meters=gf_data["radius_meters"],
            address=gf_data["address"],
            is_active=gf_data["is_active"],
            validation_required=gf_data["validation_required"]
        )
        session.add(geofence)
        created.append(gf_data["name"])
    
    await session.commit()
    
    return {
        "status": "success",
        "created": created,
        "skipped": skipped,
        "note": "Update latitude/longitude values to match actual office locations"
    }
