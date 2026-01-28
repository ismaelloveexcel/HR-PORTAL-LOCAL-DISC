"""Leave management model for tracking employee leave requests and balances.

This module integrates with the Attendance module to:
- Show accurate "On Leave" status in attendance records
- Block clock-in during approved leave periods
- Calculate leave balance deductions
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.renewal import Base


# Leave types available in UAE
LEAVE_TYPES = [
    "annual",           # Annual leave (per Article 29)
    "sick",             # Sick leave (per Article 31)
    "maternity",        # Maternity leave (per Article 30)
    "paternity",        # Paternity leave
    "compassionate",    # Bereavement/compassionate leave
    "hajj",             # Hajj leave (once during employment)
    "unpaid",           # Unpaid leave
    "study",            # Study leave
    "marriage",         # Marriage leave
    "emergency"         # Emergency leave
]

# Leave status workflow
LEAVE_STATUSES = [
    "pending",          # Awaiting approval
    "approved",         # Approved by manager
    "rejected",         # Rejected by manager
    "cancelled",        # Cancelled by employee
    "completed"         # Leave period has passed
]


class LeaveBalance(Base):
    """Employee leave balance for each leave type.
    
    Tracks entitlement, used, and remaining balance per year.
    """
    __tablename__ = "leave_balances"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    
    # Year and leave type
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    leave_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Entitlement (days per year)
    entitlement: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"), nullable=False)
    
    # Carried forward from previous year
    carried_forward: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"), nullable=False)
    
    # Used this year
    used: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"), nullable=False)
    
    # Pending (approved but not yet taken)
    pending: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"), nullable=False)
    
    # Adjusted (manual adjustments by HR)
    adjustment: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"), nullable=False)
    adjustment_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Offset days (carried over from previous year or compensatory leave)
    offset_days_used: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"), nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    @property
    def available(self) -> Decimal:
        """Calculate available leave balance including offset days.
        
        Formula: Total = Annual Entitlement + Carried Forward + Adjustment - Used - Pending
        Offset days are tracked separately but reduce from carried forward when used.
        """
        return self.entitlement + self.carried_forward + self.adjustment - self.used - self.pending


class LeaveRequest(Base):
    """Leave request submitted by employee.
    
    Workflow:
    1. Employee submits request
    2. Manager approves/rejects
    3. If approved, balance is deducted when leave starts
    4. Attendance shows "On Leave" status during leave period
    """
    __tablename__ = "leave_requests"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    
    # Leave details
    leave_type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Half-day options
    is_half_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    half_day_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # "first_half" or "second_half"
    
    # Calculated days
    total_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    
    # Reason and documentation
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # For sick certificates, etc.
    
    # Status and workflow
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    
    # Approval details
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Manager notification tracking
    manager_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    manager_notified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notification_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Validation flags
    overlaps_checked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Emergency contact during leave
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    emergency_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
