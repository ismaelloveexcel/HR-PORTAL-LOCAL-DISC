"""Employee Bank Details API routes - Restricted access with approval workflow."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Employee, EmployeeBank
from app.schemas.employee_bank import (
    EmployeeBankCreate,
    EmployeeBankUpdate,
    EmployeeBankSubmit,
    EmployeeBankResponse,
    BankVerificationRequest,
)
from app.auth.dependencies import require_auth, require_hr

router = APIRouter(prefix="/api/employees", tags=["Employee Bank Details"])


@router.get("/{employee_id}/bank", response_model=EmployeeBankResponse)
async def get_employee_bank(
    employee_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth),
):
    """Get bank details for an employee.
    
    Employees can view their own bank details.
    HR can view any employee's bank details.
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
        select(EmployeeBank).where(EmployeeBank.employee_id == employee.id)
    )
    bank = result.scalar_one_or_none()
    
    if not bank:
        bank = EmployeeBank(employee_id=employee.id)
        session.add(bank)
        await session.commit()
        await session.refresh(bank)
    
    return EmployeeBankResponse.model_validate(bank)


@router.post("/{employee_id}/bank/submit", response_model=EmployeeBankResponse)
async def submit_bank_details(
    employee_id: str,
    data: EmployeeBankSubmit,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth),
):
    """Employee submits bank details for HR validation.
    
    Employees can only submit their own bank details.
    Details are stored as pending until HR approves.
    """
    if current_user.employee_id != employee_id and current_user.role not in ["hr", "admin"]:
        raise HTTPException(status_code=403, detail="Can only submit your own bank details")
    
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    result = await session.execute(
        select(EmployeeBank).where(EmployeeBank.employee_id == employee.id)
    )
    bank = result.scalar_one_or_none()
    
    if not bank:
        bank = EmployeeBank(employee_id=employee.id)
        session.add(bank)
    
    bank.pending_bank_name = data.bank_name
    bank.pending_account_number = data.account_number
    bank.pending_iban = data.iban
    bank.pending_swift_code = data.swift_code
    bank.pending_submitted_at = datetime.now()
    bank.has_pending_changes = True
    bank.submitted_by = current_user.employee_id
    bank.submitted_at = datetime.now()
    
    await session.commit()
    await session.refresh(bank)
    
    return EmployeeBankResponse.model_validate(bank)


@router.put("/{employee_id}/bank", response_model=EmployeeBankResponse)
async def update_bank_details(
    employee_id: str,
    data: EmployeeBankUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr),
):
    """HR directly updates bank details. HR-only."""
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    result = await session.execute(
        select(EmployeeBank).where(EmployeeBank.employee_id == employee.id)
    )
    bank = result.scalar_one_or_none()
    
    if not bank:
        bank = EmployeeBank(employee_id=employee.id)
        session.add(bank)
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bank, field, value)
    
    bank.is_verified = True
    bank.verified_by = current_user.employee_id
    bank.verified_at = datetime.now()
    
    await session.commit()
    await session.refresh(bank)
    
    return EmployeeBankResponse.model_validate(bank)


@router.post("/{employee_id}/bank/verify", response_model=EmployeeBankResponse)
async def verify_bank_details(
    employee_id: str,
    request: BankVerificationRequest,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr),
):
    """Approve or reject pending bank details. HR-only."""
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    result = await session.execute(
        select(EmployeeBank).where(EmployeeBank.employee_id == employee.id)
    )
    bank = result.scalar_one_or_none()
    
    if not bank or not bank.has_pending_changes:
        raise HTTPException(status_code=400, detail="No pending changes to verify")
    
    if request.action == "approve":
        bank.bank_name = bank.pending_bank_name
        bank.account_number = bank.pending_account_number
        bank.iban = bank.pending_iban
        bank.swift_code = bank.pending_swift_code
        bank.is_verified = True
        bank.verified_by = current_user.employee_id
        bank.verified_at = datetime.now()
        from datetime import date
        bank.effective_date = date.today()
    
    bank.pending_bank_name = None
    bank.pending_account_number = None
    bank.pending_iban = None
    bank.pending_swift_code = None
    bank.pending_submitted_at = None
    bank.has_pending_changes = False
    bank.notes = request.notes
    
    await session.commit()
    await session.refresh(bank)
    
    return EmployeeBankResponse.model_validate(bank)


@router.get("/bank/pending", response_model=list[EmployeeBankResponse])
async def get_pending_bank_verifications(
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr),
):
    """Get all pending bank detail verifications. HR-only."""
    result = await session.execute(
        select(EmployeeBank).where(EmployeeBank.has_pending_changes == True)
    )
    pending = result.scalars().all()
    
    return [EmployeeBankResponse.model_validate(b) for b in pending]
