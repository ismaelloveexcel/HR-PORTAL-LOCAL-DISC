from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ActivityLogCreate(BaseModel):
    candidate_id: int
    stage: str
    action_type: str
    action_description: str
    performed_by: str
    performed_by_id: Optional[str] = None
    visibility: str = "internal"


class ActivityLogResponse(BaseModel):
    id: int
    candidate_id: int
    stage: str
    action_type: str
    action_description: str
    performed_by: str
    performed_by_id: Optional[str]
    timestamp: datetime
    visibility: str

    model_config = ConfigDict(from_attributes=True)


class ActivityLogListResponse(BaseModel):
    items: List[ActivityLogResponse]
    total: int
