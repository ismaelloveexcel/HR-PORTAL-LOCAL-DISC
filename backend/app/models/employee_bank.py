from datetime import date, datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.renewal import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class EmployeeBank(Base):
    """Bank and payroll details - Restricted access.
    
    Employees can submit their bank details, but HR must validate.
    Changes require approval workflow.
    """

    __tablename__ = "employee_bank"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    # Bank Account Details
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bank_branch: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    account_holder_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    iban: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    swift_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(10), default="AED", nullable=True)
    
    # Validation status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Submission tracking
    submitted_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Effective date (when bank details become active)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Pending changes (employee submitted but not yet approved)
    pending_bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pending_account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pending_iban: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pending_swift_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    pending_submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    has_pending_changes: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationship
    employee: Mapped["Employee"] = relationship(back_populates="bank_details")
