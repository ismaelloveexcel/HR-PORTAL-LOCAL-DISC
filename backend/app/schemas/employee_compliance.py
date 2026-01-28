from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EmployeeComplianceBase(BaseModel):
    """Base schema for employee compliance data."""
    
    # Visa Information
    visa_number: Optional[str] = None
    visa_type: Optional[str] = None
    visa_status: Optional[str] = None
    visa_issue_date: Optional[date] = None
    visa_expiry_date: Optional[date] = None
    visa_sponsor: Optional[str] = None
    
    # Emirates ID
    emirates_id_number: Optional[str] = None
    emirates_id_issue_date: Optional[date] = None
    emirates_id_expiry: Optional[date] = None
    emirates_id_status: Optional[str] = None
    
    # Medical Fitness
    medical_fitness_date: Optional[date] = None
    medical_fitness_expiry: Optional[date] = None
    medical_fitness_status: Optional[str] = None
    medical_fitness_location: Optional[str] = None
    
    # ILOE
    iloe_policy_number: Optional[str] = None
    iloe_status: Optional[str] = None
    iloe_provider: Optional[str] = None
    iloe_start_date: Optional[date] = None
    iloe_expiry: Optional[date] = None
    
    # Medical Insurance
    medical_insurance_number: Optional[str] = None
    medical_insurance_provider: Optional[str] = None
    medical_insurance_category: Optional[str] = None
    medical_insurance_start: Optional[date] = None
    medical_insurance_expiry: Optional[date] = None
    
    # Contract
    contract_type: Optional[str] = None
    contract_number: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    contract_status: Optional[str] = None
    
    # Security Clearance
    security_clearance: Optional[str] = None
    security_clearance_date: Optional[date] = None
    security_clearance_expiry: Optional[date] = None
    
    # Work Permit
    work_permit_number: Optional[str] = None
    work_permit_issue_date: Optional[date] = None
    work_permit_expiry: Optional[date] = None
    
    notes: Optional[str] = None


class EmployeeComplianceCreate(EmployeeComplianceBase):
    """Schema for creating employee compliance records."""
    employee_id: int


class EmployeeComplianceUpdate(EmployeeComplianceBase):
    """Schema for updating employee compliance records."""
    pass


class EmployeeComplianceResponse(EmployeeComplianceBase):
    """Schema for employee compliance response."""
    id: int
    employee_id: int
    last_verified_by: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed fields for expiry alerts
    visa_days_until_expiry: Optional[int] = None
    emirates_id_days_until_expiry: Optional[int] = None
    medical_fitness_days_until_expiry: Optional[int] = None
    iloe_days_until_expiry: Optional[int] = None
    contract_days_until_expiry: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class ComplianceAlertItem(BaseModel):
    """Single compliance alert item."""
    employee_id: str
    employee_name: str
    document_type: str
    expiry_date: date
    days_until_expiry: int
    status: str  # expired, expiring_soon, valid


class ComplianceAlertsResponse(BaseModel):
    """Response for compliance alerts dashboard."""
    expired: list[ComplianceAlertItem]
    expiring_30_days: list[ComplianceAlertItem]
    expiring_60_days: list[ComplianceAlertItem]
    expiring_90_days: list[ComplianceAlertItem]
    total_alerts: int
