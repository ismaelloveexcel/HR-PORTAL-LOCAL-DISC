from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.database import get_session
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeDetailResponse,
    EmployeeUpdate,
    PasswordResetRequest,
    ComplianceAlertsResponse,
)
from app.services.employees import employee_service

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get(
    "",
    response_model=List[EmployeeResponse],
    summary="List all employees",
)
async def list_employees(
    response: Response,
    active_only: bool = True,
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """List all employees. Only admin and HR can access."""
    # Cache for 60 seconds
    response.headers["Cache-Control"] = "private, max-age=60"
    return await employee_service.list_employees(session, active_only)


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
)
async def create_employee(
    data: EmployeeCreate,
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new employee.
    
    The employee's initial password will be their DOB in DDMMYYYY format.
    They must change it on first login.
    """
    return await employee_service.create_employee(session, data)


@router.post(
    "/import",
    summary="Import employees from CSV",
)
async def import_employees_csv(
    file: UploadFile = File(..., description="CSV file with employee data"),
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Import employees from a CSV file.
    
    **Supports two formats:**
    
    **1. Baynunah Employee Database format** (auto-detected):
    Columns: Employee No, Employee Name, Job Title, Department, DOB, etc.
    This format includes all employee fields like salary, line manager, probation dates.
    
    **2. Simple format** (with headers):
    ```
    employee_id,name,email,department,date_of_birth,role
    EMP001,John Smith,john@company.com,IT,15061990,viewer
    EMP002,Jane Doe,jane@company.com,HR,22031985,hr
    ```
    
    - `date_of_birth`: DDMMYYYY format or "March 11, 1979" format
    - `role`: admin, hr, or viewer (default: viewer)
    - Existing employees are skipped
    - Returns: created, skipped, errors counts
    """
    return await employee_service.import_from_csv(session, file)


@router.get(
    "/compliance/alerts",
    summary="Get compliance expiry alerts",
)
async def get_compliance_alerts(
    days: int = Query(default=60, ge=1, le=365, description="Days to look ahead"),
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Get employees with expiring compliance documents.
    
    Returns alerts grouped by urgency:
    - **expired**: Already expired documents
    - **days_7**: Expiring within 7 days
    - **days_30**: Expiring within 30 days  
    - **days_60**: Expiring within specified days (default 60)
    
    Checks: Visa, Emirates ID, Medical Fitness, ILOE, Contract
    """
    return await employee_service.get_compliance_alerts(session, days)


@router.get(
    "/{employee_id}",
    response_model=EmployeeDetailResponse,
    summary="Get employee by ID",
)
async def get_employee(
    employee_id: str,
    response: Response,
    role: str = Depends(require_role(["admin", "hr", "viewer"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific employee by their employee ID.
    
    Returns full employee details including UAE compliance fields.
    """
    # Cache for 5 minutes (employee data changes less frequently)
    response.headers["Cache-Control"] = "private, max-age=300"
    return await employee_service.get_employee(session, employee_id)


@router.put(
    "/{employee_id}",
    response_model=EmployeeDetailResponse,
    summary="Update employee",
)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Update an employee's information.
    
    Only HR and Admin can update employee data.
    All fields are optional - only provided fields will be updated.
    
    **UAE Compliance fields:**
    - visa_number, visa_issue_date, visa_expiry_date
    - emirates_id_number, emirates_id_expiry
    - medical_fitness_date, medical_fitness_expiry
    - iloe_status, iloe_expiry
    - contract_type, contract_start_date, contract_end_date
    """
    return await employee_service.update_employee(session, employee_id, data)


@router.post(
    "/bulk-update",
    summary="Bulk update employees from CSV",
)
async def bulk_update_employees_csv(
    file: UploadFile = File(..., description="CSV file with employee data"),
    update_layer: str = Query(
        default="employee",
        description="Which layer to update: employee, compliance, bank, or all"
    ),
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Bulk update existing employees from a CSV file.
    
    **Matches by Employee ID and updates existing records.**
    
    **Layer options:**
    - `employee`: Updates core employee fields (name, job_title, department, etc.)
    - `compliance`: Updates UAE compliance fields (visa, emirates_id, medical, etc.)
    - `bank`: Updates bank account details
    - `all`: Updates all layers based on CSV columns
    
    **CSV format:**
    - First column must be `employee_id` or `Employee No`
    - Include any fields you want to update
    - Empty cells are skipped (won't overwrite existing data)
    
    **Example compliance columns:**
    visa_number, visa_issue_date, visa_expiry_date, emirates_id_number, emirates_id_expiry,
    medical_fitness_date, medical_fitness_expiry, iloe_status, iloe_expiry
    
    **Example bank columns:**
    bank_name, account_name, account_number, iban, swift_code, routing_number
    """
    return await employee_service.bulk_update_from_csv(session, file, update_layer)


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset employee password to DOB",
)
async def reset_password(
    request: PasswordResetRequest,
    role: str = Depends(require_role(["admin"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Reset an employee's password back to their DOB.
    
    Only admins can perform this action.
    The employee will need to set a new password on next login.
    """
    success = await employee_service.reset_password(session, request.employee_id)
    return {"success": success, "message": "Password reset to DOB"}


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_200_OK,
    summary="Deactivate an employee",
)
async def deactivate_employee(
    employee_id: str,
    role: str = Depends(require_role(["admin"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Deactivate an employee account.
    
    The employee will no longer be able to log in.
    Only admins can perform this action.
    """
    success = await employee_service.deactivate_employee(session, employee_id)
    return {"success": success, "message": "Employee deactivated"}


@router.get(
    "/export",
    summary="Export employees to CSV",
)
async def export_employees(
    active_only: bool = Query(default=True, description="Export only active employees"),
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Export all employees to CSV with complete data (compliance, bank, contact).
    
    Returns a downloadable CSV file with all employee fields including:
    - Core employee data (name, email, department, job title)
    - Compliance data (visa, Emirates ID, medical, ILOE, contract)
    - Bank details (bank name, IBAN, account number)
    
    **Query parameters:**
    - `active_only`: true (default) exports only active employees, false exports all
    """
    from fastapi.responses import StreamingResponse
    from io import BytesIO
    
    csv_content = await employee_service.export_to_csv(session, active_only)
    
    # Create streaming response
    output = BytesIO(csv_content.encode('utf-8'))
    filename = f"employees_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post(
    "/bulk-update-json",
    summary="Bulk update employees (JSON)",
)
async def bulk_update_employees(
    updates: List[dict],
    role: str = Depends(require_role(["admin", "hr"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Bulk update multiple employees at once (JSON body).
    
    Updates department, manager, status, job title, and location for multiple employees.
    
    **Request body format:**
    ```json
    [
        {
            "employee_id": "EMP001",
            "department": "IT",
            "job_title": "Senior Developer",
            "line_manager_name": "Jane Smith",
            "employment_status": "Active",
            "location": "Abu Dhabi"
        },
        {
            "employee_id": "EMP002",
            "department": "HR",
            "employment_status": "On Leave"
        }
    ]
    ```
    
    **Returns:**
    - `updated`: Count of successfully updated employees
    - `not_found`: Count of employees not found
    - `errors`: List of error messages (max 20)
    """
    return await employee_service.bulk_update_employees(session, updates)


@router.get(
    "/search",
    response_model=List[EmployeeResponse],
    summary="Advanced employee search",
)
async def search_employees(
    q: str = Query(default="", description="Search query (name, employee_id, email, department)"),
    department: str = Query(default=None, description="Filter by department"),
    status: str = Query(default=None, description="Filter by status (active/inactive)"),
    role: str = Depends(require_role(["admin", "hr", "viewer"])),
    session: AsyncSession = Depends(get_session),
):
    """
    Advanced search for employees.
    
    **Search capabilities:**
    - Search by name, employee ID, email, or department (case-insensitive)
    - Filter by specific department
    - Filter by employment status (active/inactive)
    
    **Examples:**
    - `/api/employees/search?q=john` - Find employees named John
    - `/api/employees/search?department=IT` - All IT department employees
    - `/api/employees/search?q=EMP001` - Find by employee ID
    - `/api/employees/search?department=IT&status=active` - Active IT employees
    """
    return await employee_service.search_employees(session, q, department, status)
