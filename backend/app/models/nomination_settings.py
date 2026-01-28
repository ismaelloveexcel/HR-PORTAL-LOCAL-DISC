from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.renewal import Base


class NominationSettings(Base):
    """Settings for the Employee of the Year nomination period"""

    __tablename__ = "nomination_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    is_open: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    announcement_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    invitation_email_subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    invitation_email_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_email_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    emails_sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
