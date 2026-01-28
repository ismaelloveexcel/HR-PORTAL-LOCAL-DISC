from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EmployeeBankBase(BaseModel):
    """Base schema for employee bank details."""
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    iban: Optional[str] = None
    swift_code: Optional[str] = None
    currency: Optional[str] = "AED"


class EmployeeBankCreate(EmployeeBankBase):
    """Schema for creating employee bank records."""
    employee_id: int


class EmployeeBankUpdate(EmployeeBankBase):
    """Schema for updating employee bank records."""
    pass


class EmployeeBankSubmit(EmployeeBankBase):
    """Schema for employee submitting bank details (requires HR validation)."""
    pass


class EmployeeBankResponse(EmployeeBankBase):
    """Schema for employee bank response."""
    id: int
    employee_id: int
    is_verified: bool
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    submitted_by: Optional[str] = None
    submitted_at: Optional[datetime] = None
    effective_date: Optional[date] = None
    
    # Pending changes (for self-service workflow)
    pending_bank_name: Optional[str] = None
    pending_account_number: Optional[str] = None
    pending_iban: Optional[str] = None
    pending_swift_code: Optional[str] = None
    pending_submitted_at: Optional[datetime] = None
    has_pending_changes: bool = False
    
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BankVerificationRequest(BaseModel):
    """Request to verify or reject bank details."""
    action: str = Field(..., pattern="^(approve|reject)$")
    notes: Optional[str] = None
