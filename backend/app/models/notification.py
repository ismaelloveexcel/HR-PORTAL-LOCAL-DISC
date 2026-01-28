from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.employee import Base

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=True)
    link: Mapped[str] = mapped_column(String(255), nullable=True)
