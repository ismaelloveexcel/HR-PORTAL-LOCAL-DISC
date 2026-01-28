from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.renewal import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class OnboardingToken(Base):
    """Secure token for new joiner onboarding.
    
    When HR creates a new employee, a unique token is generated that can be
    shared with the employee. They can use this token (via a link) to complete
    their profile without needing to log in first.
    """

    __tablename__ = "onboarding_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Token details
    token: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Status
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Expiry
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Tracking
    created_by: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    # Optional: track how many times accessed (for security monitoring)
    access_count: Mapped[int] = mapped_column(default=0, nullable=False)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    employee: Mapped["Employee"] = relationship(back_populates="onboarding_tokens")
    
    @property
    def is_valid(self) -> bool:
        """Check if token is still valid (not used and not expired)."""
        if self.is_used:
            return False
        if datetime.now(self.expires_at.tzinfo) > self.expires_at:
            return False
        return True
