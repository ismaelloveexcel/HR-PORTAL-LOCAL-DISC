"""Employee Compliance API routes - HR-only access for UAE compliance data."""

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Employee, EmployeeCompliance
from app.schemas.employee_compliance import (
    EmployeeComplianceCreate,
    EmployeeComplianceUpdate,
    EmployeeComplianceResponse,
    ComplianceAlertItem,
    ComplianceAlertsResponse,
)
from app.auth.dependencies import require_auth, require_hr

router = APIRouter(prefix="/api/employees", tags=["Employee Compliance"])


def calculate_days_until_expiry(expiry_date: Optional[date]) -> Optional[int]:
    """Calculate days until a date expires."""
    if not expiry_date:
        return None
    return (expiry_date - date.today()).days


def get_expiry_status(days: Optional[int]) -> str:
    """Get status based on days until expiry."""
    if days is None:
        return "unknown"
    if days < 0:
        return "expired"
    if days <= 30:
        return "expiring_soon"
    if days <= 60:
        return "expiring_60"
    if days <= 90:
        return "expiring_90"
    return "valid"


@router.get("/{employee_id}/compliance", response_model=EmployeeComplianceResponse)
async def get_employee_compliance(
    employee_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth),
):
    """Get compliance data for an employee.
    
    Employees can view their own compliance data.
    HR can view any employee's compliance data.
    """
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if current_user.role not in ["hr", "admin"] and current_user.employee_id != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await session.execute(
        select(EmployeeCompliance).where(EmployeeCompliance.employee_id == employee.id)
    )
    compliance = result.scalar_one_or_none()
    
    if not compliance:
        compliance = EmployeeCompliance(employee_id=employee.id)
        session.add(compliance)
        await session.commit()
        await session.refresh(compliance)
    
    response = EmployeeComplianceResponse.model_validate(compliance)
    response.visa_days_until_expiry = calculate_days_until_expiry(compliance.visa_expiry_date)
    response.emirates_id_days_until_expiry = calculate_days_until_expiry(compliance.emirates_id_expiry)
    response.medical_fitness_days_until_expiry = calculate_days_until_expiry(compliance.medical_fitness_expiry)
    response.iloe_days_until_expiry = calculate_days_until_expiry(compliance.iloe_expiry)
    response.contract_days_until_expiry = calculate_days_until_expiry(compliance.contract_end_date)
    
    return response


@router.put("/{employee_id}/compliance", response_model=EmployeeComplianceResponse)
async def update_employee_compliance(
    employee_id: str,
    data: EmployeeComplianceUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr),
):
    """Update compliance data for an employee. HR-only."""
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    result = await session.execute(
        select(EmployeeCompliance).where(EmployeeCompliance.employee_id == employee.id)
    )
    compliance = result.scalar_one_or_none()
    
    if not compliance:
        compliance = EmployeeCompliance(employee_id=employee.id)
        session.add(compliance)
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(compliance, field, value)
    
    from datetime import datetime
    compliance.last_verified_by = current_user.employee_id
    compliance.last_verified_at = datetime.now()
    
    await session.commit()
    await session.refresh(compliance)
    
    response = EmployeeComplianceResponse.model_validate(compliance)
    response.visa_days_until_expiry = calculate_days_until_expiry(compliance.visa_expiry_date)
    response.emirates_id_days_until_expiry = calculate_days_until_expiry(compliance.emirates_id_expiry)
    response.medical_fitness_days_until_expiry = calculate_days_until_expiry(compliance.medical_fitness_expiry)
    response.iloe_days_until_expiry = calculate_days_until_expiry(compliance.iloe_expiry)
    response.contract_days_until_expiry = calculate_days_until_expiry(compliance.contract_end_date)
    
    return response


@router.get("/compliance/alerts", response_model=ComplianceAlertsResponse)
async def get_compliance_alerts(
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr),
):
    """Get compliance alerts dashboard. HR-only.
    
    Returns all employees with expired or expiring documents.
    """
    today = date.today()
    days_30 = today + timedelta(days=30)
    days_60 = today + timedelta(days=60)
    days_90 = today + timedelta(days=90)
    
    result = await session.execute(
        select(EmployeeCompliance, Employee)
        .join(Employee, EmployeeCompliance.employee_id == Employee.id)
        .where(Employee.is_active == True)
    )
    records = result.all()
    
    expired = []
    expiring_30 = []
    expiring_60 = []
    expiring_90 = []
    
    def add_alert(emp: Employee, comp: EmployeeCompliance, doc_type: str, expiry: Optional[date]):
        if not expiry:
            return
        days = (expiry - today).days
        alert = ComplianceAlertItem(
            employee_id=emp.employee_id,
            employee_name=emp.name,
            document_type=doc_type,
            expiry_date=expiry,
            days_until_expiry=days,
            status=get_expiry_status(days),
        )
        if days < 0:
            expired.append(alert)
        elif days <= 30:
            expiring_30.append(alert)
        elif days <= 60:
            expiring_60.append(alert)
        elif days <= 90:
            expiring_90.append(alert)
    
    for compliance, employee in records:
        add_alert(employee, compliance, "Visa", compliance.visa_expiry_date)
        add_alert(employee, compliance, "Emirates ID", compliance.emirates_id_expiry)
        add_alert(employee, compliance, "Medical Fitness", compliance.medical_fitness_expiry)
        add_alert(employee, compliance, "ILOE Insurance", compliance.iloe_expiry)
        add_alert(employee, compliance, "Medical Insurance", compliance.medical_insurance_expiry)
        add_alert(employee, compliance, "Contract", compliance.contract_end_date)
        add_alert(employee, compliance, "Work Permit", compliance.work_permit_expiry)
        add_alert(employee, compliance, "Security Clearance", compliance.security_clearance_expiry)
    
    expired.sort(key=lambda x: x.days_until_expiry)
    expiring_30.sort(key=lambda x: x.days_until_expiry)
    expiring_60.sort(key=lambda x: x.days_until_expiry)
    expiring_90.sort(key=lambda x: x.days_until_expiry)
    
    return ComplianceAlertsResponse(
        expired=expired,
        expiring_30_days=expiring_30,
        expiring_60_days=expiring_60,
        expiring_90_days=expiring_90,
        total_alerts=len(expired) + len(expiring_30) + len(expiring_60) + len(expiring_90),
    )
