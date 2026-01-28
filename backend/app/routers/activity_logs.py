from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.activity_log import ActivityLogResponse
from app.services.activity_log import activity_log_service

router = APIRouter(prefix="/activity-logs", tags=["activity-logs"])


@router.get(
    "/candidate/{candidate_id}",
    response_model=List[ActivityLogResponse],
    summary="Get candidate-visible activity logs",
)
async def get_candidate_logs(
    candidate_id: int,
    include_internal: bool = Query(False, description="Include internal logs (HR only)"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get activity logs for a candidate.
    
    By default, only returns logs with visibility='candidate'.
    Set include_internal=true to see all logs (requires HR/Admin role).
    """
    logs = await activity_log_service.get_candidate_logs(
        session, candidate_id, include_internal
    )
    return logs
