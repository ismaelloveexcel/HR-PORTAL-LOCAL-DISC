from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class TemplateBase(BaseModel):
    name: str = Field(..., max_length=120)
    type: str = Field(..., max_length=30)
    content: str
    revision_note: Optional[str] = None
    parent_id: Optional[int] = None

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(TemplateBase):
    is_active: Optional[bool] = True

class TemplateResponse(TemplateBase):
    id: int
    version: int
    created_by: str
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
