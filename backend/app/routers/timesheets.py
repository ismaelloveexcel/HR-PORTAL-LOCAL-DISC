"""Timesheet management router."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
import jwt
from jwt.exceptions import PyJWTError
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database import get_session
from app.models.employee import Employee
from app.models.timesheet import Timesheet, TIMESHEET_STATUSES
from app.schemas.timesheet import (
    TimesheetSummary, TimesheetResponse, TimesheetSubmit,
    TimesheetApproval, TimesheetList, MonthlyAttendanceAnalytics
)
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/timesheets", tags=["Timesheets"])


async def get_current_employee(
    authorization: str = Header(...),
    session: AsyncSession = Depends(get_session)
) -> Employee:
    """Extract and validate employee from JWT token."""
    try:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header",
            )
        settings = get_settings()
        payload = jwt.decode(token, settings.auth_secret_key, algorithms=["HS256"])
        employee_id = payload.get("sub")
        if not employee_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        result = await session.execute(
            select(Employee).where(Employee.id == int(employee_id))
        )
        employee = result.scalar_one_or_none()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")


def build_timesheet_response(timesheet: Timesheet, employee_name: Optional[str] = None) -> TimesheetResponse:
    """Build timesheet response from model."""
    return TimesheetResponse(
        id=timesheet.id,
        employee_id=timesheet.employee_id,
        employee_name=employee_name,
        year=timesheet.year,
        month=timesheet.month,
        status=timesheet.status,
        total_working_days=timesheet.total_working_days,
        total_present_days=timesheet.total_present_days,
        total_absent_days=timesheet.total_absent_days,
        total_leave_days=timesheet.total_leave_days,
        total_wfh_days=timesheet.total_wfh_days,
        total_late_arrivals=timesheet.total_late_arrivals,
        total_early_departures=timesheet.total_early_departures,
        total_regular_hours=timesheet.total_regular_hours,
        total_overtime_hours=timesheet.total_overtime_hours,
        total_night_overtime_hours=timesheet.total_night_overtime_hours,
        total_holiday_overtime_hours=timesheet.total_holiday_overtime_hours,
        total_overtime_amount=timesheet.total_overtime_amount,
        offset_hours_earned=timesheet.offset_hours_earned,
        offset_hours_used=timesheet.offset_hours_used,
        days_at_head_office=timesheet.days_at_head_office,
        days_at_kezad=timesheet.days_at_kezad,
        days_at_safario=timesheet.days_at_safario,
        days_at_sites=timesheet.days_at_sites,
        days_at_meeting=timesheet.days_at_meeting,
        days_at_event=timesheet.days_at_event,
        food_allowance_days=timesheet.food_allowance_days,
        food_allowance_total=timesheet.food_allowance_total,
        has_compliance_issues=timesheet.has_compliance_issues,
        compliance_notes=timesheet.compliance_notes,
        submitted_at=timesheet.submitted_at,
        employee_notes=timesheet.employee_notes,
        manager_approved_by=timesheet.manager_approved_by,
        manager_approved_at=timesheet.manager_approved_at,
        manager_notes=timesheet.manager_notes,
        hr_approved_by=timesheet.hr_approved_by,
        hr_approved_at=timesheet.hr_approved_at,
        hr_notes=timesheet.hr_notes,
        rejected_by=timesheet.rejected_by,
        rejected_at=timesheet.rejected_at,
        rejection_reason=timesheet.rejection_reason,
        exported_at=timesheet.exported_at,
        payroll_reference=timesheet.payroll_reference,
        created_at=timesheet.created_at,
        updated_at=timesheet.updated_at
    )


@router.get("/statuses")
async def get_timesheet_statuses():
    """Get list of timesheet statuses."""
    return {
        "statuses": TIMESHEET_STATUSES,
        "descriptions": {
            "draft": "Auto-generated, not yet submitted",
            "submitted": "Submitted by employee for approval",
            "manager_approved": "Approved by line manager",
            "hr_approved": "Final approval by HR",
            "rejected": "Rejected, needs correction",
            "exported": "Exported to payroll system"
        }
    }


@router.post("/generate/{employee_id}", response_model=TimesheetResponse)
async def generate_timesheet(
    employee_id: int,
    year: int = Query(..., description="Year"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Generate or regenerate timesheet from attendance records."""
    if current_user.role not in ["admin", "hr"] and current_user.id != employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get employee
    emp_result = await session.execute(
        select(Employee).where(Employee.id == employee_id)
    )
    employee = emp_result.scalar_one_or_none()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    service = AttendanceService(session)
    timesheet = await service.generate_monthly_timesheet(employee_id, year, month)
    
    return build_timesheet_response(timesheet, employee.name)


@router.get("/{timesheet_id}", response_model=TimesheetResponse)
async def get_timesheet(
    timesheet_id: int,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Get a specific timesheet."""
    result = await session.execute(
        select(Timesheet, Employee).join(
            Employee, Timesheet.employee_id == Employee.id
        ).where(Timesheet.id == timesheet_id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    timesheet, employee = row
    
    if current_user.role not in ["admin", "hr"] and current_user.id != timesheet.employee_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return build_timesheet_response(timesheet, employee.name)


@router.post("/{timesheet_id}/submit", response_model=TimesheetResponse)
async def submit_timesheet(
    timesheet_id: int,
    submit: TimesheetSubmit,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Submit timesheet for approval."""
    result = await session.execute(
        select(Timesheet).where(Timesheet.id == timesheet_id)
    )
    timesheet = result.scalar_one_or_none()
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.employee_id != current_user.id and current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Can only submit your own timesheet")
    
    if timesheet.status not in ["draft", "rejected"]:
        raise HTTPException(status_code=400, detail=f"Cannot submit timesheet in {timesheet.status} status")
    
    timesheet.status = "submitted"
    timesheet.submitted_at = datetime.now(timezone.utc)
    timesheet.employee_notes = submit.employee_notes
    
    await session.commit()
    await session.refresh(timesheet)
    
    return build_timesheet_response(timesheet)


@router.post("/{timesheet_id}/manager-approve", response_model=TimesheetResponse)
async def manager_approve_timesheet(
    timesheet_id: int,
    approval: TimesheetApproval,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Manager approval of timesheet."""
    if current_user.role not in ["admin", "hr", "manager"]:
        raise HTTPException(status_code=403, detail="Only managers can approve timesheets")
    
    result = await session.execute(
        select(Timesheet).where(Timesheet.id == timesheet_id)
    )
    timesheet = result.scalar_one_or_none()
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.status != "submitted":
        raise HTTPException(status_code=400, detail="Timesheet must be submitted before manager approval")
    
    # Verify manager relationship for non-HR
    if current_user.role == "manager":
        emp_result = await session.execute(
            select(Employee).where(Employee.id == timesheet.employee_id)
        )
        employee = emp_result.scalar_one_or_none()
        if not employee or employee.line_manager_id != current_user.id:
            raise HTTPException(status_code=403, detail="Can only approve timesheets for your direct reports")
    
    now = datetime.now(timezone.utc)
    
    if approval.approved:
        timesheet.status = "manager_approved"
        timesheet.manager_approved_by = current_user.id
        timesheet.manager_approved_at = now
        timesheet.manager_notes = approval.notes
    else:
        timesheet.status = "rejected"
        timesheet.rejected_by = current_user.id
        timesheet.rejected_at = now
        timesheet.rejection_reason = approval.rejection_reason
    
    await session.commit()
    await session.refresh(timesheet)
    
    return build_timesheet_response(timesheet)


@router.post("/{timesheet_id}/hr-approve", response_model=TimesheetResponse)
async def hr_approve_timesheet(
    timesheet_id: int,
    approval: TimesheetApproval,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """HR final approval of timesheet."""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only HR can give final approval")
    
    result = await session.execute(
        select(Timesheet).where(Timesheet.id == timesheet_id)
    )
    timesheet = result.scalar_one_or_none()
    
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    if timesheet.status != "manager_approved":
        raise HTTPException(status_code=400, detail="Timesheet must have manager approval before HR approval")
    
    now = datetime.now(timezone.utc)
    
    if approval.approved:
        timesheet.status = "hr_approved"
        timesheet.hr_approved_by = current_user.id
        timesheet.hr_approved_at = now
        timesheet.hr_notes = approval.notes
    else:
        timesheet.status = "rejected"
        timesheet.rejected_by = current_user.id
        timesheet.rejected_at = now
        timesheet.rejection_reason = approval.rejection_reason
    
    await session.commit()
    await session.refresh(timesheet)
    
    return build_timesheet_response(timesheet)


@router.get("/list/{year}/{month}", response_model=TimesheetList)
async def list_timesheets(
    year: int,
    month: int,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """List timesheets for a month (HR/Admin sees all, managers see team, employees see own)."""
    query = select(Timesheet).where(
        and_(
            Timesheet.year == year,
            Timesheet.month == month
        )
    )
    
    if current_user.role not in ["admin", "hr"]:
        if current_user.role == "manager":
            # Get team members
            team_result = await session.execute(
                select(Employee.id).where(Employee.line_manager_id == current_user.id)
            )
            team_ids = [r for r in team_result.scalars().all()]
            team_ids.append(current_user.id)
            query = query.where(Timesheet.employee_id.in_(team_ids))
        else:
            query = query.where(Timesheet.employee_id == current_user.id)
    
    if status_filter:
        query = query.where(Timesheet.status == status_filter)
    
    result = await session.execute(query)
    timesheets = result.scalars().all()
    
    # Count by status
    pending = sum(1 for t in timesheets if t.status in ["draft", "submitted"])
    approved = sum(1 for t in timesheets if t.status in ["manager_approved", "hr_approved", "exported"])
    rejected = sum(1 for t in timesheets if t.status == "rejected")
    
    return TimesheetList(
        year=year,
        month=month,
        total_count=len(timesheets),
        pending_count=pending,
        approved_count=approved,
        rejected_count=rejected,
        timesheets=[
            TimesheetSummary(
                id=t.id,
                employee_id=t.employee_id,
                year=t.year,
                month=t.month,
                status=t.status,
                total_working_days=t.total_working_days,
                total_present_days=t.total_present_days,
                total_absent_days=t.total_absent_days,
                total_leave_days=t.total_leave_days,
                total_wfh_days=t.total_wfh_days,
                total_late_arrivals=t.total_late_arrivals,
                total_early_departures=t.total_early_departures,
                total_regular_hours=t.total_regular_hours,
                total_overtime_hours=t.total_overtime_hours,
                total_night_overtime_hours=t.total_night_overtime_hours,
                total_holiday_overtime_hours=t.total_holiday_overtime_hours,
                total_overtime_amount=t.total_overtime_amount,
                offset_hours_earned=t.offset_hours_earned,
                offset_hours_used=t.offset_hours_used,
                days_at_head_office=t.days_at_head_office,
                days_at_kezad=t.days_at_kezad,
                days_at_safario=t.days_at_safario,
                days_at_sites=t.days_at_sites,
                days_at_meeting=t.days_at_meeting,
                days_at_event=t.days_at_event,
                food_allowance_days=t.food_allowance_days,
                food_allowance_total=t.food_allowance_total,
                has_compliance_issues=t.has_compliance_issues,
                compliance_notes=t.compliance_notes
            )
            for t in timesheets
        ]
    )


@router.get("/analytics/{year}/{month}")
async def get_monthly_analytics(
    year: int,
    month: int,
    current_user: Employee = Depends(get_current_employee),
    session: AsyncSession = Depends(get_session)
):
    """Get monthly attendance analytics (HR/Admin only)."""
    if current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Only HR/Admin can view analytics")
    
    service = AttendanceService(session)
    return await service.get_monthly_analytics(year, month)
