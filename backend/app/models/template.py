from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.employee import Base

class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)  # document, letter, checklist, timeline, pass
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("templates.id"), nullable=True)
    created_by: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    revision_note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    parent: Mapped[Optional["Template"]] = relationship("Template", remote_side=[id], backref="revisions")
