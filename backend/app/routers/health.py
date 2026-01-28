import hashlib
import json
import os
import secrets
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, Body, Header
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_role
from app.database import get_session

router = APIRouter(prefix="/health", tags=["health"])

MAINTENANCE_SECRET = os.environ.get("MAINTENANCE_SECRET", "")
ADMIN_EMPLOYEE_ID = os.environ.get("ADMIN_EMPLOYEE_ID", "BAYN00008")
# Admin DOB password in DDMMYYYY format - this is the expected initial password
# that users must change on first login. Not a security risk as it's DOB-based.
ADMIN_DOB_PASSWORD = os.environ.get("ADMIN_DOB_PASSWORD", "16051988")
SYSTEM_ADMIN_ID = "ADMIN001"
SYSTEM_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


@router.get("/ping", summary="Simple health ping (no auth)")
async def ping():
    """
    Ultra-simple health check for Azure startup probe.
    No authentication, no database, just returns OK immediately.
    Used by Azure to verify the app is running.
    """
    from app.core.config import get_settings
    settings = get_settings()
    version_info = settings.get_version_info()
    
    return {
        "status": "ok",
        "message": "pong",
        **version_info
    }


@router.get("/revision", summary="Deployment revision and version info (no auth)")
async def get_revision():
    """
    Returns detailed deployment and version information.
    Shows git commit, build timestamp, and environment info.
    No authentication required - useful for verifying deployments.
    """
    from pathlib import Path
    from app.core.config import get_settings
    
    settings = get_settings()
    version_info = settings.get_version_info()
    
    # Try to read build_info.txt if it exists
    build_info = {}
    build_info_path = Path(__file__).parent.parent.parent / "build_info.txt"
    if build_info_path.exists():
        try:
            with open(build_info_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        build_info[key.lower()] = value
        except (IOError, UnicodeDecodeError) as e:
            # Log the error but continue gracefully
            build_info = {"error": "Failed to read build_info.txt"}
    
    return {
        "status": "ok",
        "revision": {
            **version_info,
            "build_info": build_info if build_info else "not available",
            "app_name": settings.app_name,
        }
    }


@router.get("", summary="API healthcheck")
async def healthcheck(role: str = Depends(require_role())):
    return {"status": "ok", "role": role}


@router.post("/seed-admin", summary="Create admin user if not exists (emergency use)")
async def seed_admin(
    secret_token: str = Header(..., alias="X-Admin-Secret"),
    session: AsyncSession = Depends(get_session),
):
    """
    Emergency endpoint to create admin users if they don't exist.
    Requires X-Admin-Secret header matching AUTH_SECRET_KEY environment variable.
    """
    from sqlalchemy import text
    import logging
    from app.core.config import get_settings

    logger = logging.getLogger(__name__)
    settings = get_settings()

    # Verify secret token
    if secret_token != settings.auth_secret_key:
        logger.warning("Unauthorized seed attempt")
        raise HTTPException(status_code=403, detail="Invalid secret token")

    try:
        results = []

        # Create BAYN00008 (main admin)
        ADMIN_PASSWORD_HASH = "3543bc93f69b085852270bb3edfac94a:7e8f4f92a9b90a1260bc005304f5b30f014dd4603056cacb0b6170d05049b832"

        # Check if BAYN00008 exists
        check = await session.execute(text("SELECT employee_id FROM employees WHERE employee_id = 'BAYN00008'"))
        if not check.fetchone():
            await session.execute(
                text("""
                    INSERT INTO employees (employee_id, name, email, department, date_of_birth, role, is_active, employment_status, password_hash, password_changed, profile_status)
                    VALUES ('BAYN00008', 'Ismael Espinoza', 'ismael.espinoza@baynunah.ae', 'IT', '1988-05-16', 'admin', true, 'Active', :hash, false, 'complete')
                """),
                {"hash": ADMIN_PASSWORD_HASH}
            )
            results.append("Created BAYN00008 (Ismael Espinoza)")
        else:
            results.append("BAYN00008 already exists")

        await session.commit()

        return {
            "success": True,
            "results": results,
            "login_credentials": {
                "BAYN00008": "16051988"
            },
            "note": "BAYN00008 is the only admin account"
        }

    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Seed admin failed: {error_type} - {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Seed failed: {error_type} - {str(e)}"
        )


@router.post("/reset-admin-password", summary="Reset admin password to default (emergency use)")
async def reset_admin_password(
    secret_token: str = Header(..., alias="X-Admin-Secret"),
    session: AsyncSession = Depends(get_session),
):
    """
    Emergency endpoint to reset BAYN00008 admin password to default (DOB: 16051988).
    Requires X-Admin-Secret header matching AUTH_SECRET_KEY environment variable.

    This is useful when:
    - Startup migrations fail
    - Admin password gets corrupted
    - Database is in inconsistent state

    Returns employee details after successful reset.
    """
    from sqlalchemy import text
    import logging
    from app.core.config import get_settings

    logger = logging.getLogger(__name__)
    settings = get_settings()

    # Verify secret token
    if secret_token != settings.auth_secret_key:
        logger.warning("Unauthorized admin password reset attempt")
        raise HTTPException(status_code=403, detail="Invalid secret token")

    try:
        # Reset admin password
        ADMIN_EMPLOYEE_ID = "BAYN00008"
        ADMIN_PASSWORD_HASH = "3543bc93f69b085852270bb3edfac94a:7e8f4f92a9b90a1260bc005304f5b30f014dd4603056cacb0b6170d05049b832"

        result = await session.execute(
            text("""
                UPDATE employees
                SET password_hash = :hash,
                    password_changed = false,
                    role = 'admin',
                    is_active = true,
                    employment_status = 'Active'
                WHERE employee_id = :emp_id
                RETURNING employee_id, name, role, is_active
            """),
            {"hash": ADMIN_PASSWORD_HASH, "emp_id": ADMIN_EMPLOYEE_ID}
        )

        row = result.fetchone()
        await session.commit()

        if row:
            # Audit log for security monitoring (generic message)
            logger.info("Admin account password reset completed")
            return {
                "success": True,
                "message": f"Password reset for {row[0]} - {row[1]}",
                "employee_id": row[0],
                "name": row[1],
                "role": row[2],
                "is_active": row[3],
                "default_password": ADMIN_DOB_PASSWORD,
                "instructions": "You can now login with this employee_id and the default_password"
            }
        else:
            # Generic error for security (don't reveal specifics)
            logger.error("Admin account reset failed - account not found")
            return {
                "success": False,
                "message": f"Employee {ADMIN_EMPLOYEE_ID} not found in database",
                "suggestion": "Database may need to be seeded. Check startup migration logs."
            }

    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Admin password reset failed: {error_type}")
        # Note: Traceback intentionally not logged to avoid sensitive data exposure
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Password reset failed: {error_type}"
        )


@router.get("/db", summary="Database connectivity and admin account check")
async def health_check_db(session: AsyncSession = Depends(get_session)):
    """
    Check database connectivity and return admin account status.
    
    Returns:
    - Database connection status
    - Total employee count
    - Admin account existence and status
    
    Use this to diagnose login issues before attempting password reset.
    """
    from sqlalchemy import text
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Test basic query
        result = await session.execute(text("SELECT COUNT(*) FROM employees"))
        employee_count = result.scalar()
        
        # Check admin exists
        admin_result = await session.execute(
            text("""
                SELECT employee_id, name, role, is_active, password_changed, employment_status 
                FROM employees 
                WHERE employee_id = 'BAYN00008'
            """)
        )
        admin = admin_result.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "employee_count": employee_count,
            "admin_check": {
                "exists": admin is not None,
                "details": {
                    "employee_id": admin[0],
                    "name": admin[1],
                    "role": admin[2],
                    "is_active": admin[3],
                    "password_changed": admin[4],
                    "employment_status": admin[5]
                } if admin else None,
                "note": "If admin doesn't exist or is_active is false, use /api/health/reset-admin-password"
            }
        }
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Database health check failed: {error_type}")
        # Note: Traceback intentionally not logged to avoid sensitive data exposure
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {error_type}"
        )


@router.get("/list-employees", summary="List employees for diagnostics")
async def list_employees_diagnostic(
    token: str = Query(..., description="Secure maintenance token"),
    session: AsyncSession = Depends(get_session),
):
    """List employees for production diagnostics."""
    if not MAINTENANCE_SECRET:
        raise HTTPException(status_code=503, detail="Maintenance endpoint not configured")
    
    if not secrets.compare_digest(token, MAINTENANCE_SECRET):
        raise HTTPException(status_code=403, detail="Invalid maintenance token")
    
    result = await session.execute(
        text("SELECT employee_id, name, role FROM employees ORDER BY employee_id LIMIT 20")
    )
    employees = [{"employee_id": r[0], "name": r[1], "role": r[2]} for r in result.fetchall()]
    
    count_result = await session.execute(text("SELECT COUNT(*) FROM employees"))
    total = count_result.scalar()
    
    return {"total_employees": total, "sample": employees}


@router.post("/fix-production", summary="One-time production data fix")
async def fix_production_data(
    token: str = Query(..., description="Secure maintenance token from environment"),
    session: AsyncSession = Depends(get_session),
):
    """
    One-time endpoint to fix production data issues.
    Requires MAINTENANCE_SECRET environment variable.
    """
    if not MAINTENANCE_SECRET:
        raise HTTPException(status_code=503, detail="Maintenance endpoint not configured")
    
    if not secrets.compare_digest(token, MAINTENANCE_SECRET):
        raise HTTPException(status_code=403, detail="Invalid maintenance token")
    
    results = {"employment_status": {}, "admin": {}}
    
    # 1. Check current employment_status values
    check_result = await session.execute(
        text("SELECT DISTINCT employment_status, COUNT(*) as cnt FROM employees GROUP BY employment_status ORDER BY cnt DESC")
    )
    results["employment_status"]["before"] = {row[0]: row[1] for row in check_result.fetchall()}
    
    # 2. Normalize employment_status to 'Active'
    update_result = await session.execute(
        text("""
            UPDATE employees 
            SET employment_status = 'Active' 
            WHERE LOWER(TRIM(COALESCE(employment_status, ''))) = 'active' 
            AND (employment_status IS NULL OR employment_status != 'Active')
        """)
    )
    results["employment_status"]["normalized"] = update_result.rowcount if hasattr(update_result, 'rowcount') else 0
    
    # 2.5. Check if is_active column exists and set it for all active employees
    has_is_active = False
    try:
        is_active_check = await session.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'employees' AND column_name = 'is_active'
            """)
        )
        has_is_active = is_active_check.fetchone() is not None
        results["schema"] = {"has_is_active_column": has_is_active}
        
        if has_is_active:
            # Ensure is_active matches employment_status for Active employees
            is_active_fix = await session.execute(
                text("""
                    UPDATE employees 
                    SET is_active = true 
                    WHERE LOWER(TRIM(COALESCE(employment_status, ''))) = 'active'
                    AND (is_active IS NULL OR is_active = false)
                """)
            )
            results["schema"]["is_active_fixed"] = is_active_fix.rowcount if hasattr(is_active_fix, 'rowcount') else 0
    except Exception as e:
        results["schema"] = {"error": str(e)}
    
    # 3. Check admin user
    admin_check = await session.execute(
        text("SELECT id, name, role, password_hash FROM employees WHERE employee_id = :emp_id"),
        {"emp_id": ADMIN_EMPLOYEE_ID}
    )
    admin_row = admin_check.fetchone()
    
    if admin_row:
        results["admin"]["found"] = True
        results["admin"]["name"] = admin_row[1]
        results["admin"]["current_role"] = admin_row[2]
        results["admin"]["employee_id"] = ADMIN_EMPLOYEE_ID
        results["admin"]["expected_password"] = ADMIN_DOB_PASSWORD
        
        # Check if password works
        current_hash = admin_row[3]
        results["admin"]["has_password_hash"] = current_hash is not None
        results["admin"]["hash_format_valid"] = False
        password_works = False
        
        if current_hash:
            results["admin"]["hash_length"] = len(current_hash)
            try:
                parts = current_hash.split(':')
                results["admin"]["hash_parts"] = len(parts)
                if len(parts) == 2:
                    results["admin"]["hash_format_valid"] = True
                    salt, stored_key = parts
                    key = hashlib.pbkdf2_hmac('sha256', ADMIN_DOB_PASSWORD.encode(), salt.encode(), 100000)
                    password_works = (key.hex() == stored_key)
            except Exception as e:
                results["admin"]["hash_error"] = str(e)
        
        results["admin"]["password_valid"] = password_works
        
        # ALWAYS fix admin password to ensure it works
        # Generate new password hash for DOB password
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac('sha256', ADMIN_DOB_PASSWORD.encode(), salt.encode(), 100000)
        new_hash = f"{salt}:{key.hex()}"
        
        await session.execute(
            text("""
                UPDATE employees 
                SET password_hash = :hash, password_changed = false, role = 'admin'
                WHERE employee_id = :emp_id
            """),
            {"hash": new_hash, "emp_id": ADMIN_EMPLOYEE_ID}
        )
        results["admin"]["fixed"] = True
        results["admin"]["new_password"] = ADMIN_DOB_PASSWORD
        
        # Also ensure admin is_active if column exists
        if has_is_active:
            await session.execute(
                text("UPDATE employees SET is_active = true WHERE employee_id = :emp_id"),
                {"emp_id": ADMIN_EMPLOYEE_ID}
            )
            results["admin"]["is_active_set"] = True
    else:
        results["admin"]["found"] = False
        results["admin"]["error"] = f"Employee {ADMIN_EMPLOYEE_ID} not found in database"
        # List available employees for debugging
        all_emp = await session.execute(text("SELECT employee_id, name FROM employees LIMIT 5"))
        results["admin"]["sample_employees"] = [{"id": r[0], "name": r[1]} for r in all_emp.fetchall()]
    
    # 3.5. Also fix ADMIN001 (System Admin) - used by frontend admin login
    results["system_admin"] = {}
    sys_admin_check = await session.execute(
        text("SELECT id, name, role, password_hash FROM employees WHERE employee_id = :emp_id"),
        {"emp_id": SYSTEM_ADMIN_ID}
    )
    sys_admin_row = sys_admin_check.fetchone()
    
    if sys_admin_row:
        results["system_admin"]["found"] = True
        results["system_admin"]["name"] = sys_admin_row[1]
        results["system_admin"]["employee_id"] = SYSTEM_ADMIN_ID
        
        # Generate new password hash using ADMIN_PASSWORD from env (or default)
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac('sha256', SYSTEM_ADMIN_PASSWORD.encode(), salt.encode(), 100000)
        new_hash = f"{salt}:{key.hex()}"
        
        await session.execute(
            text("""
                UPDATE employees 
                SET password_hash = :hash, password_changed = false, role = 'admin'
                WHERE employee_id = :emp_id
            """),
            {"hash": new_hash, "emp_id": SYSTEM_ADMIN_ID}
        )
        results["system_admin"]["fixed"] = True
        results["system_admin"]["password_set_to"] = "value from ADMIN_PASSWORD env var (or 'admin123' if not set)"
        
        # Also ensure is_active if column exists
        if has_is_active:
            await session.execute(
                text("UPDATE employees SET is_active = true WHERE employee_id = :emp_id"),
                {"emp_id": SYSTEM_ADMIN_ID}
            )
            results["system_admin"]["is_active_set"] = True
    else:
        results["system_admin"]["found"] = False
        results["system_admin"]["note"] = "ADMIN001 not found - frontend admin login may not work"
    
    await session.commit()
    
    # 4. Backfill line_manager_id from line_manager_name (for nominations)
    results["line_manager"] = {}
    try:
        # Check how many need backfilling
        missing_check = await session.execute(
            text("""
                SELECT COUNT(*) FROM employees 
                WHERE line_manager_name IS NOT NULL 
                AND line_manager_name != ''
                AND line_manager_id IS NULL
            """)
        )
        results["line_manager"]["missing_before"] = missing_check.scalar() or 0
        
        # Backfill by matching names
        backfill_result = await session.execute(
            text("""
                UPDATE employees e
                SET line_manager_id = m.id
                FROM employees m
                WHERE e.line_manager_name IS NOT NULL 
                AND e.line_manager_name != ''
                AND e.line_manager_id IS NULL
                AND LOWER(TRIM(e.line_manager_name)) = LOWER(TRIM(m.name))
            """)
        )
        results["line_manager"]["backfilled"] = backfill_result.rowcount if hasattr(backfill_result, 'rowcount') else 0
        
        # Also try with normalized whitespace
        backfill_fuzzy = await session.execute(
            text("""
                UPDATE employees e
                SET line_manager_id = m.id
                FROM employees m
                WHERE e.line_manager_name IS NOT NULL 
                AND e.line_manager_name != ''
                AND e.line_manager_id IS NULL
                AND LOWER(regexp_replace(e.line_manager_name, '\\s+', ' ', 'g')) = 
                    LOWER(regexp_replace(m.name, '\\s+', ' ', 'g'))
            """)
        )
        results["line_manager"]["backfilled_fuzzy"] = backfill_fuzzy.rowcount if hasattr(backfill_fuzzy, 'rowcount') else 0
        
        await session.commit()
        
        # Check remaining
        still_missing = await session.execute(
            text("""
                SELECT COUNT(*) FROM employees 
                WHERE line_manager_name IS NOT NULL 
                AND line_manager_name != ''
                AND line_manager_id IS NULL
            """)
        )
        results["line_manager"]["still_missing"] = still_missing.scalar() or 0
        
    except Exception as e:
        results["line_manager"]["error"] = str(e)
    
    # 5. Verify managers now show (safely handle missing columns)
    try:
        # Check if the newer columns exist before querying them
        column_check = await session.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'employees' 
                AND column_name IN ('line_manager_id', 'is_active', 'function')
            """)
        )
        existing_columns = {row[0] for row in column_check.fetchall()}
        
        if {'line_manager_id', 'is_active', 'function'}.issubset(existing_columns):
            manager_check = await session.execute(
                text("""
                    SELECT COUNT(DISTINCT e.line_manager_id) 
                    FROM employees e 
                    WHERE e.line_manager_id IS NOT NULL 
                    AND e.is_active = true 
                    AND LOWER(TRIM(e.employment_status)) = 'active'
                    AND LOWER(TRIM(e.function)) IN ('officer', 'coordinator', 'skilled labour', 'non skilled labour')
                """)
            )
            results["managers_with_eligible_reports"] = manager_check.scalar() or 0
        else:
            results["managers_with_eligible_reports"] = "skipped - schema not fully migrated"
            results["missing_columns"] = list({'line_manager_id', 'is_active', 'function'} - existing_columns)
    except Exception as e:
        results["managers_with_eligible_reports"] = f"skipped - {str(e)}"
    
    return {"success": True, "fixes_applied": results}


async def _export_table(session: AsyncSession, table_name: str) -> List[Dict[str, Any]]:
    """Export all rows from a table as a list of dicts.
    
    Security: Uses static SQL queries mapped by table name to prevent SQL injection.
    Only allowed tables can be exported.
    """
    # Use static query mapping to completely eliminate SQL injection risk
    TABLE_QUERIES = {
        "employees": 'SELECT * FROM "employees"',
        "candidates": 'SELECT * FROM "candidates"',
        "recruitment_requests": 'SELECT * FROM "recruitment_requests"',
        "passes": 'SELECT * FROM "passes"',
    }
    
    if table_name not in TABLE_QUERIES:
        raise ValueError(f"Table {table_name} not in allowlist")
    
    # Get column names using parameterized query
    cols_result = await session.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name = :table ORDER BY ordinal_position"
    ), {"table": table_name})
    columns = [r[0] for r in cols_result.fetchall()]
    
    # Get all rows using static query from allowlist
    data_result = await session.execute(text(TABLE_QUERIES[table_name]))
    rows = []
    for row in data_result.fetchall():
        row_dict = {}
        for i, col in enumerate(columns):
            val = row[i]
            # Convert datetime/date to string for JSON serialization
            if hasattr(val, 'isoformat'):
                val = val.isoformat()
            row_dict[col] = val
        rows.append(row_dict)
    return rows


@router.get("/export-data", summary="Export data for sync to production")
async def export_data(
    token: str = Query(..., description="Secure maintenance token"),
    session: AsyncSession = Depends(get_session),
):
    """
    Export Employees, Recruitment, and Passes data for production sync.
    Returns JSON data that can be imported into production.
    """
    if not MAINTENANCE_SECRET:
        raise HTTPException(status_code=503, detail="Maintenance endpoint not configured")
    
    if not secrets.compare_digest(token, MAINTENANCE_SECRET):
        raise HTTPException(status_code=403, detail="Invalid maintenance token")
    
    export = {
        "employees": await _export_table(session, "employees"),
        "candidates": await _export_table(session, "candidates"),
        "recruitment_requests": await _export_table(session, "recruitment_requests"),
        "passes": await _export_table(session, "passes"),
    }
    
    return {
        "success": True,
        "counts": {k: len(v) for k, v in export.items()},
        "data": export
    }


ALLOWED_COLUMNS = {
    "employees": {"id", "employee_id", "name", "email", "department", "date_of_birth", 
                  "password_hash", "password_changed", "role", "is_active", "job_title", 
                  "function", "location", "work_schedule", "gender", "nationality", 
                  "company_phone", "employment_status", "line_manager_id", "created_at", "updated_at"},
    "candidates": {"id", "candidate_number", "recruitment_request_id", "pass_number", "full_name",
                   "email", "phone", "current_position", "current_company", "years_experience",
                   "expected_salary", "notice_period_days", "source", "source_details", "resume_path",
                   "linkedin_url", "status", "stage", "stage_changed_at", "rejection_reason", "notes",
                   "emirates_id", "visa_status", "created_at", "updated_at", "current_location",
                   "willing_to_relocate", "has_driving_license", "preferred_contact_method", "timezone",
                   "industry_function", "availability_date", "current_salary", "salary_currency",
                   "salary_negotiable", "portfolio_url", "documents", "core_skills", "programming_languages",
                   "hardware_platforms", "protocols_tools", "recruiter_notes", "interview_observations",
                   "risk_flags", "visa_expiry_date", "current_country", "details_confirmed_by_candidate",
                   "details_confirmed_at", "last_updated_by", "entity", "references_list", "soft_skills",
                   "technical_skills", "pass_id", "ai_ranking", "skills_match_score", "education_level",
                   "screening_rank", "cv_scoring", "resume_url", "cv_scored_at", "pass_token",
                   "score_breakdown", "hr_rating", "manager_rating", "last_activity_at"},
    "recruitment_requests": {"id", "request_number", "position_title", "department", "hiring_manager_id",
                              "requested_by", "request_date", "target_hire_date", "headcount", 
                              "employment_type", "job_description", "requirements", "salary_range_min",
                              "salary_range_max", "status", "approval_status", "manager_pass_number",
                              "created_at", "updated_at", "hiring_manager_employee_id", 
                              "requested_by_employee_id", "manager_pass_id", "required_skills", "priority",
                              "expected_start_date", "location", "experience_min", "experience_max",
                              "education_level", "benefits", "reporting_to"},
    "passes": {"id", "pass_number", "pass_type", "full_name", "email", "phone", "department",
               "position", "valid_from", "valid_until", "access_areas", "purpose", "sponsor_name",
               "status", "is_printed", "employee_id", "created_by", "created_at", "updated_at",
               "linked_employee_id", "created_by_employee_id"},
}


async def _get_table_columns(session: AsyncSession, table_name: str) -> set:
    """Query information_schema to get actual columns in the target database table."""
    result = await session.execute(
        text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = :table_name AND table_schema = 'public'
        """),
        {"table_name": table_name}
    )
    return {row[0] for row in result.fetchall()}


async def _import_table(session: AsyncSession, table_name: str, rows: List[Dict[str, Any]], 
                        conflict_column: str = "id") -> Dict[str, Any]:
    """Import rows into a table with upsert logic. Uses allowlist AND schema introspection for safety."""
    imported = 0
    errors = []
    
    allowed = ALLOWED_COLUMNS.get(table_name, set())
    if not allowed:
        return {"imported": 0, "errors": [f"Unknown table: {table_name}"]}
    
    # Get actual columns from target database schema
    actual_columns = await _get_table_columns(session, table_name)
    if not actual_columns:
        return {"imported": 0, "errors": [f"Table {table_name} not found or has no columns"]}
    
    # Only use columns that are both allowed AND exist in target schema
    valid_columns = allowed & actual_columns
    
    for row in rows:
        try:
            # Filter to only valid columns (allowed + exists in target)
            safe_row = {k: v for k, v in row.items() if k in valid_columns}
            if not safe_row:
                continue
            
            columns = list(safe_row.keys())
            col_names = ", ".join(columns)
            placeholders = ", ".join([f":{c}" for c in columns])
            
            # Build update clause (exclude conflict column)
            update_cols = [c for c in columns if c != conflict_column]
            update_clause = ", ".join([f"{c} = EXCLUDED.{c}" for c in update_cols])
            
            sql = f"""
                INSERT INTO {table_name} ({col_names})
                VALUES ({placeholders})
                ON CONFLICT ({conflict_column}) DO UPDATE SET {update_clause}
            """
            await session.execute(text(sql), safe_row)
            imported += 1
        except Exception as e:
            errors.append(f"{table_name} row {row.get(conflict_column, '?')}: {str(e)[:100]}")
    
    return {"imported": imported, "errors": errors}


@router.post("/seed-all-employees", summary="Force seed all employees from seed file")
async def seed_all_employees(
    secret_token: str = Header(..., alias="X-Admin-Secret"),
    session: AsyncSession = Depends(get_session),
):
    """
    Force load all employees from seed_employees.json.
    This will clear existing employees and load fresh data.
    Requires X-Admin-Secret header matching AUTH_SECRET_KEY environment variable.
    """
    import logging
    from app.core.config import get_settings

    logger = logging.getLogger(__name__)
    settings = get_settings()

    # Verify secret token
    if secret_token != settings.auth_secret_key:
        logger.warning("Unauthorized seed attempt")
        raise HTTPException(status_code=403, detail="Invalid secret token")

    try:
        # Load seed file
        seed_file = os.path.join(os.path.dirname(__file__), '..', 'seed_employees.json')
        if not os.path.exists(seed_file):
            raise HTTPException(status_code=404, detail=f"Seed file not found: {seed_file}")

        with open(seed_file, 'r') as f:
            employees = json.load(f)

        logger.info(f"Loaded {len(employees)} employees from seed file")

        # Clear existing employees (to avoid conflicts)
        await session.execute(text("DELETE FROM employees"))
        logger.info("Cleared existing employees")

        # First, check what columns exist in the table
        col_result = await session.execute(
            text("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'employees' AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
        )
        db_columns = {row[0]: row[1] for row in col_result.fetchall()}
        logger.info(f"Database columns: {db_columns}")

        # Insert all employees with minimal required columns
        inserted = 0
        errors = []
        from datetime import datetime, date

        for emp in employees:
            try:
                # Convert date_of_birth string to date object for asyncpg
                dob = emp.get('date_of_birth')
                if dob and isinstance(dob, str):
                    dob = datetime.strptime(dob, '%Y-%m-%d').date()

                await session.execute(
                    text("""
                        INSERT INTO employees (
                            id, employee_id, name, email, department, date_of_birth,
                            password_hash, password_changed, role, is_active,
                            employment_status, profile_status
                        ) VALUES (
                            :id, :employee_id, :name, :email, :department,
                            :date_of_birth,
                            :password_hash, :password_changed, :role, :is_active,
                            :employment_status, :profile_status
                        )
                    """),
                    {
                        'id': emp['id'],
                        'employee_id': emp['employee_id'],
                        'name': emp['name'],
                        'email': emp.get('email'),
                        'department': emp.get('department'),
                        'date_of_birth': dob,
                        'password_hash': emp['password_hash'],
                        'password_changed': bool(emp.get('password_changed', False)),
                        'role': emp.get('role', 'viewer'),
                        'is_active': bool(emp.get('is_active', True)),
                        'employment_status': emp.get('employment_status', 'Active'),
                        'profile_status': emp.get('profile_status', 'complete')
                    }
                )
                inserted += 1
            except Exception as e:
                errors.append(f"{emp['employee_id']}: {str(e)[:150]}")

        # Now update line_manager_id references
        manager_updates = 0
        for emp in employees:
            if emp.get('line_manager_id'):
                try:
                    await session.execute(
                        text("UPDATE employees SET line_manager_id = :mgr_id WHERE employee_id = :emp_id"),
                        {'mgr_id': emp['line_manager_id'], 'emp_id': emp['employee_id']}
                    )
                    manager_updates += 1
                except Exception:
                    pass  # Ignore manager update errors

        # Reset sequence to max id
        if employees:
            max_id = max(emp['id'] for emp in employees)
            await session.execute(
                text("SELECT setval('employees_id_seq', :max_id, true)"),
                {"max_id": max_id}
            )

        await session.commit()

        return {
            "success": True,
            "total_in_seed": len(employees),
            "inserted": inserted,
            "db_columns": list(db_columns.keys()),
            "errors": errors[:10] if errors else [],
            "message": f"Successfully loaded {inserted} employees from seed file"
        }

    except HTTPException:
        raise
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Seed all employees failed: {error_type} - {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Seed failed: {error_type} - {str(e)}"
        )


@router.post("/import-data", summary="Import data from development")
async def import_data(
    token: str = Query(..., description="Secure maintenance token"),
    data: Dict[str, Any] = Body(..., description="Data to import"),
    session: AsyncSession = Depends(get_session),
):
    """
    Import Employees, Recruitment, and Passes data from development.
    Receives JSON data from export-data endpoint.
    """
    if not MAINTENANCE_SECRET:
        raise HTTPException(status_code=503, detail="Maintenance endpoint not configured")
    
    if not secrets.compare_digest(token, MAINTENANCE_SECRET):
        raise HTTPException(status_code=403, detail="Invalid maintenance token")
    
    results = {}
    all_errors = []
    
    try:
        # Import in order: employees first (others may depend on them)
        for table_name, conflict_col in [
            ("employees", "employee_id"),
            ("recruitment_requests", "id"),
            ("candidates", "id"),
            ("passes", "id"),
        ]:
            if table_name in data:
                result = await _import_table(session, table_name, data[table_name], conflict_col)
                results[table_name] = result["imported"]
                all_errors.extend(result["errors"])
        
        await session.commit()
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    
    return {"success": True, "imported": results, "errors": all_errors[:20]}
