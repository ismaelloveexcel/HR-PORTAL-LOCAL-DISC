from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class NotificationBase(BaseModel):
    user_id: Optional[str] = None
    title: str
    message: str
    type: Optional[str] = None
    link: Optional[str] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
