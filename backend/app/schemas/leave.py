"""Leave management schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class LeaveBalanceResponse(BaseModel):
    """Leave balance for a specific leave type."""
    id: int
    employee_id: int
    year: int
    leave_type: str
    entitlement: Decimal
    carried_forward: Decimal
    used: Decimal
    pending: Decimal
    adjustment: Decimal
    adjustment_reason: Optional[str] = None
    offset_days_used: Decimal = Decimal("0")
    available: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class LeaveBalanceSummary(BaseModel):
    """Summary of all leave balances for an employee."""
    employee_id: int
    employee_name: str
    year: int
    balances: List[LeaveBalanceResponse] = []


class LeaveRequestCreate(BaseModel):
    """Create a new leave request."""
    leave_type: str = Field(..., description="Type of leave: annual, sick, maternity, etc.")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    is_half_day: bool = Field(default=False, description="Is this a half-day leave?")
    half_day_type: Optional[str] = Field(default=None, description="first_half or second_half")
    reason: Optional[str] = Field(default=None, description="Reason for leave")
    emergency_contact: Optional[str] = Field(default=None, description="Emergency contact name")
    emergency_phone: Optional[str] = Field(default=None, description="Emergency contact phone")


class LeaveRequestResponse(BaseModel):
    """Leave request response."""
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    leave_type: str
    start_date: date
    end_date: date
    is_half_day: bool
    half_day_type: Optional[str] = None
    total_days: Decimal
    reason: Optional[str] = None
    document_url: Optional[str] = None
    status: str
    approved_by: Optional[int] = None
    approver_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    manager_notified: bool = False
    notification_sent_at: Optional[datetime] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LeaveApprovalRequest(BaseModel):
    """Approve or reject a leave request."""
    approved: bool = Field(..., description="True to approve, False to reject")
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection")


class LeaveCalendarEntry(BaseModel):
    """Calendar entry for leave display."""
    employee_id: int
    employee_name: str
    leave_type: str
    start_date: date
    end_date: date
    status: str
    is_half_day: bool = False
    is_holiday: bool = False


class PublicHolidayResponse(BaseModel):
    """Public holiday response."""
    id: int
    name: str
    name_arabic: Optional[str] = None
    start_date: date
    end_date: date
    year: int
    holiday_type: str
    is_paid: bool
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
