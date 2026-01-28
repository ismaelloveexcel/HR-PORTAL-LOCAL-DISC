"""Timesheet schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class TimesheetSummary(BaseModel):
    """Timesheet summary data."""
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    year: int
    month: int
    status: str
    
    # Attendance summary
    total_working_days: int
    total_present_days: int
    total_absent_days: int
    total_leave_days: Decimal
    total_wfh_days: int
    total_late_arrivals: int
    total_early_departures: int
    
    # Hours summary
    total_regular_hours: Decimal
    total_overtime_hours: Decimal
    total_night_overtime_hours: Decimal
    total_holiday_overtime_hours: Decimal
    total_overtime_amount: Decimal
    
    # Offset hours
    offset_hours_earned: Decimal
    offset_hours_used: Decimal
    
    # Location breakdown
    days_at_head_office: int
    days_at_kezad: int
    days_at_safario: int
    days_at_sites: int
    days_at_meeting: int
    days_at_event: int
    
    # Food allowance
    food_allowance_days: int
    food_allowance_total: Decimal
    
    # Compliance
    has_compliance_issues: bool
    compliance_notes: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class TimesheetResponse(TimesheetSummary):
    """Full timesheet response with approval details."""
    submitted_at: Optional[datetime] = None
    employee_notes: Optional[str] = None
    
    manager_approved_by: Optional[int] = None
    manager_approver_name: Optional[str] = None
    manager_approved_at: Optional[datetime] = None
    manager_notes: Optional[str] = None
    
    hr_approved_by: Optional[int] = None
    hr_approver_name: Optional[str] = None
    hr_approved_at: Optional[datetime] = None
    hr_notes: Optional[str] = None
    
    rejected_by: Optional[int] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    exported_at: Optional[datetime] = None
    payroll_reference: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime


class TimesheetSubmit(BaseModel):
    """Submit timesheet for approval."""
    employee_notes: Optional[str] = Field(default=None, description="Notes from employee")


class TimesheetApproval(BaseModel):
    """Approve or reject timesheet."""
    approved: bool = Field(..., description="True to approve, False to reject")
    notes: Optional[str] = Field(default=None, description="Approval/rejection notes")
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection")


class TimesheetList(BaseModel):
    """List of timesheets."""
    year: int
    month: int
    total_count: int
    pending_count: int
    approved_count: int
    rejected_count: int
    timesheets: List[TimesheetSummary] = []


class MonthlyAttendanceAnalytics(BaseModel):
    """Monthly attendance analytics."""
    year: int
    month: int
    total_employees: int
    
    # Attendance metrics
    avg_present_rate: Decimal  # Percentage
    avg_late_arrivals: Decimal
    avg_overtime_hours: Decimal
    
    # Location distribution
    head_office_percentage: Decimal
    kezad_percentage: Decimal
    safario_percentage: Decimal
    sites_percentage: Decimal
    wfh_percentage: Decimal
    
    # Overtime breakdown
    total_regular_overtime: Decimal
    total_night_overtime: Decimal
    total_holiday_overtime: Decimal
    total_overtime_cost: Decimal
    
    # Compliance
    employees_with_issues: int
    compliance_rate: Decimal  # Percentage
