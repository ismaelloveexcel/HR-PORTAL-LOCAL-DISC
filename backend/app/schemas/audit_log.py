from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class AuditLogBase(BaseModel):
    action: str
    entity: str
    entity_id: Optional[int] = None
    user_id: Optional[str] = None
    details: Optional[str] = None

class AuditLogResponse(AuditLogBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
