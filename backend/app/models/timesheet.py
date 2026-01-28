"""Timesheet model for monthly attendance summary and approval workflow.

This module provides:
- Monthly timesheet generation from attendance records
- Manager approval workflow
- Payroll export integration
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.renewal import Base


# Timesheet status workflow
TIMESHEET_STATUSES = [
    "draft",            # Auto-generated, not yet submitted
    "submitted",        # Submitted by employee
    "manager_approved", # Approved by line manager
    "hr_approved",      # Final approval by HR
    "rejected",         # Rejected (needs correction)
    "exported"          # Exported to payroll
]


class Timesheet(Base):
    """Monthly timesheet summary for an employee.
    
    Auto-generated from daily attendance records at month end.
    Requires manager approval before payroll processing.
    """
    __tablename__ = "timesheets"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False, index=True)
    
    # Period
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Summary totals (auto-calculated from attendance records)
    total_working_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_present_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_absent_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_leave_days: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"), nullable=False)
    total_wfh_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_late_arrivals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_early_departures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Hours breakdown
    total_regular_hours: Mapped[Decimal] = mapped_column(Numeric(7, 2), default=Decimal("0"), nullable=False)
    total_overtime_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"), nullable=False)
    total_night_overtime_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"), nullable=False)
    total_holiday_overtime_hours: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"), nullable=False)
    
    # Overtime amounts (for Paid policy employees)
    total_overtime_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"), nullable=False)
    
    # Offset balance changes (for Offset policy employees)
    offset_hours_earned: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"), nullable=False)
    offset_hours_used: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"), nullable=False)
    
    # Location breakdown
    days_at_head_office: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    days_at_kezad: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    days_at_safario: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    days_at_sites: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    days_at_meeting: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    days_at_event: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Food allowance
    food_allowance_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    food_allowance_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"), nullable=False)
    
    # Compliance flags
    has_compliance_issues: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    compliance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status and workflow
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    
    # Employee submission
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    employee_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Manager approval
    manager_approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), nullable=True)
    manager_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    manager_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # HR approval
    hr_approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), nullable=True)
    hr_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    hr_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Rejection
    rejected_by: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Payroll export
    exported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    payroll_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
