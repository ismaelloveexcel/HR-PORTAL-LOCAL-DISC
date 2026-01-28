#!/usr/bin/env python3
"""
Import employees from Baynunah Employee Database CSV.

Usage:
    cd backend
    uv run python ../scripts/import_employees.py ../Employees-Employee\ Database-\ Github.csv

This script:
1. Reads the CSV with the actual Baynunah column headers
2. Transforms data (dates, numbers, etc.)
3. Creates employee records with all extended fields
4. Handles duplicates gracefully (skips existing employee_ids)
"""

import asyncio
import csv
import sys
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

# Add parent to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine
from app.models.employee import Employee
from app.services.employees import hash_password


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse various date formats from CSV."""
    if not date_str or date_str.strip() == "":
        return None
    
    date_str = date_str.strip()
    
    # Try various formats
    formats = [
        "%B %d, %Y",      # "March 11, 1979"
        "%d/%m/%Y",       # "11/03/1979"
        "%Y-%m-%d",       # "1979-03-11"
        "%m/%d/%Y",       # "03/11/1979"
        "%d-%m-%Y",       # "11-03-1979"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    print(f"  Warning: Could not parse date '{date_str}'")
    return None


def parse_decimal(value_str: Optional[str]) -> Optional[Decimal]:
    """Parse decimal value from CSV."""
    if not value_str or value_str.strip() == "":
        return None
    
    try:
        # Remove commas and convert
        clean = value_str.strip().replace(",", "")
        return Decimal(clean)
    except (InvalidOperation, ValueError):
        return None


def parse_int(value_str: Optional[str]) -> Optional[int]:
    """Parse integer value from CSV."""
    if not value_str or value_str.strip() == "":
        return None
    
    try:
        # Handle float strings like "22.0" or "NaN"
        clean = value_str.strip()
        if clean.lower() == "nan":
            return None
        return int(float(clean))
    except (ValueError, TypeError):
        return None


def map_employment_status(status: Optional[str]) -> str:
    """Map employment status to standard values."""
    if not status:
        return "Active"
    
    status_lower = status.lower().strip()
    mapping = {
        "active": "Active",
        "terminated": "Terminated",
        "resigned": "Resigned",
        "consultant": "Consultant",
        "pending": "Pending",
        "backed out": "Backed Out",
        "outsourced": "Outsourced",
        "freelancer": "Freelancer",
    }
    return mapping.get(status_lower, status)


def map_probation_status(status: Optional[str]) -> Optional[str]:
    """Map probation status to standard values."""
    if not status:
        return None
    
    status_lower = status.lower().strip()
    mapping = {
        "confirmed": "Confirmed",
        "under probation": "Under Probation",
        "not yet joined": "Not Yet Joined",
        "n/a": None,
    }
    return mapping.get(status_lower, status)


async def import_employees(csv_path: str, update_existing: bool = False):
    """Import employees from CSV file.
    
    Args:
        csv_path: Path to the CSV file
        update_existing: If True, update existing employee records; if False, skip them
    """
    
    print(f"Reading CSV file: {csv_path}")
    print(f"Update mode: {'UPDATE existing records' if update_existing else 'SKIP existing records'}")
    
    # Read CSV with UTF-8-BOM encoding (Excel exported)
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Found {len(rows)} rows in CSV")
    
    stats = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": 0,
    }
    
    async with AsyncSessionLocal() as session:
        for row in rows:
            employee_id = row.get("Employee No", "").strip()
            name = row.get("Employee Name", "").strip()
            
            if not employee_id or not name:
                print(f"  Skipping row with missing ID or name: {row}")
                stats["errors"] += 1
                continue
            
            # Check if employee already exists
            result = await session.execute(
                select(Employee).where(Employee.employee_id == employee_id)
            )
            existing = result.scalar_one_or_none()
            
            if existing and not update_existing:
                print(f"  Skipping existing employee: {employee_id} ({name})")
                stats["skipped"] += 1
                continue
            
            # Parse date of birth - required for password
            dob = parse_date(row.get("DOB"))
            if not dob:
                # Use a default DOB if not provided
                dob = date(1990, 1, 1)
                print(f"  Warning: No DOB for {employee_id}, using default")
            
            # Create password from DOB
            password_hash = hash_password(dob.strftime("%d%m%Y"))
            
            # Parse joining date for probation dates
            joining_date = parse_date(row.get("Joining Date"))
            probation_start = joining_date
            
            # Determine role based on job title/function
            job_title = row.get("Job Title", "").strip()
            function = row.get("Function", "").strip()
            role = "viewer"  # Default role
            if "HR" in (row.get("Department") or ""):
                role = "hr"
            if function.lower() in ["executive", "director"]:
                role = "hr"  # Give senior staff HR access
            
            # Create employee record
            employee = Employee(
                employee_id=employee_id,
                name=name,
                email=row.get("Company Email Address", "").strip() or None,
                department=row.get("Department", "").strip() or None,
                date_of_birth=dob,
                password_hash=password_hash,
                password_changed=False,
                role=role,
                is_active=map_employment_status(row.get("Employment Status")) == "Active",
                
                # Job info
                job_title=job_title or None,
                function=function or None,
                location=row.get("Location", "").strip() or None,
                work_schedule=row.get("Work Schedule", "").strip() or None,
                
                # Personal info
                gender=row.get("Gender", "").strip() or None,
                nationality=row.get("Nationality", "").strip() or None,
                company_phone=row.get("Company Phone Number", "").strip() or None,
                
                # Line manager
                line_manager_name=row.get("Line Manager", "").strip() or None,
                line_manager_email=row.get("Line Manager's Email (from Line Manager)", "").strip() or None,
                
                # Employment dates
                joining_date=joining_date,
                last_promotion_date=parse_date(row.get("Last Promotion Date")),
                last_increment_date=parse_date(row.get("Last Increment Date")),
                
                # Probation
                probation_start_date=probation_start,
                one_month_eval_date=parse_date(row.get("1 Month Eval Date")),
                three_month_eval_date=parse_date(row.get("3 Month Eval Date")),
                six_month_eval_date=parse_date(row.get("6 Month Eval Date")),
                probation_status=map_probation_status(row.get("Probation Status")),
                
                # Employment status
                employment_status=map_employment_status(row.get("Employment Status")),
                years_of_service=parse_int(row.get("Years of Service")),
                
                # Leave and overtime
                annual_leave_entitlement=parse_int(row.get("Annual Leave Entitlement")),
                overtime_type=row.get("Overtime Type", "").strip() or None,
                
                # Compliance
                security_clearance=row.get("Security Clearance", "").strip() or None,
                visa_status=row.get("Visa Status", "").strip() or None,
                
                # Medical insurance
                medical_insurance_provider=row.get("Medical Insurance Provider", "").strip() or None,
                medical_insurance_category=row.get("Medical Insurance Category", "").strip() or None,
                
                # Compensation
                basic_salary=parse_decimal(row.get("Basic Salary")),
                housing_allowance=parse_decimal(row.get("Housing")),
                transportation_allowance=parse_decimal(row.get("Transportation")),
                air_ticket_entitlement=parse_decimal(row.get("Air Ticket Entitlement")),
                other_allowance=parse_decimal(row.get("Other Allowance")),
                consultancy_fees=parse_decimal(row.get("Consultancy Fees")),
                air_fare_allowance=parse_decimal(row.get("Air Fare Allowance")),
                family_air_ticket_allowance=parse_decimal(row.get("Family Air Ticket Allowance")),
                net_salary=parse_decimal(row.get("Net Salary")),
                
                # Profile status
                profile_status="incomplete",
            )
            
            session.add(employee)
            stats["created"] += 1
            print(f"  Created: {employee_id} - {name} ({role})")
        
        await session.commit()
    
    print("\n--- Import Summary ---")
    print(f"  Created: {stats['created']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"  Errors:  {stats['errors']}")
    print(f"  Total:   {len(rows)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_employees.py <csv_file>")
        print("  Example: python import_employees.py '../Employees-Employee Database- Github.csv'")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    
    asyncio.run(import_employees(csv_path))
