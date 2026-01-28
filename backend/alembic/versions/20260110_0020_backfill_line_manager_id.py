"""Backfill line_manager_id from line_manager_name

Revision ID: 20260110_0020
Revises: 20260109_0022
Create Date: 2026-01-10

This migration links employees to their line managers by matching the
line_manager_name field to existing employees. This is required for
the Employee of the Year nomination system to identify managers with
eligible direct reports.
"""
from alembic import op
import sqlalchemy as sa

revision = '20260110_0020'
down_revision = '20260109_0022'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    
    # Backfill line_manager_id by matching line_manager_name to employee names
    # This enables the nominations system to find managers with eligible reports
    result = conn.execute(sa.text("""
        UPDATE employees e
        SET line_manager_id = m.id
        FROM employees m
        WHERE e.line_manager_name IS NOT NULL 
        AND e.line_manager_name != ''
        AND e.line_manager_id IS NULL
        AND LOWER(TRIM(e.line_manager_name)) = LOWER(TRIM(m.name))
    """))
    
    # Also try partial matching for cases like "John Smith" vs "John  Smith" (extra spaces)
    conn.execute(sa.text("""
        UPDATE employees e
        SET line_manager_id = m.id
        FROM employees m
        WHERE e.line_manager_name IS NOT NULL 
        AND e.line_manager_name != ''
        AND e.line_manager_id IS NULL
        AND LOWER(regexp_replace(e.line_manager_name, '\\s+', ' ', 'g')) = 
            LOWER(regexp_replace(m.name, '\\s+', ' ', 'g'))
    """))
    
    # Ensure is_active=true for all employees with employment_status='Active'
    conn.execute(sa.text("""
        UPDATE employees 
        SET is_active = true 
        WHERE LOWER(TRIM(COALESCE(employment_status, ''))) = 'active'
        AND (is_active IS NULL OR is_active = false)
    """))


def downgrade():
    # Don't clear line_manager_id on downgrade - data preservation
    pass
