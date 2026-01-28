from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.employee import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=True)
