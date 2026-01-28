"""
Revision ID: 20260103_0007_add_indexes_for_employee_and_renewal
Revises: 20250102_0006_add_attendance_records_table
Create Date: 2026-01-03

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260103_0007_add_indexes_for_employee_and_renewal'
down_revision = '20250102_0006'
branch_labels = None
depends_on = None

def upgrade():
    op.create_index('idx_employees_email', 'employees', ['email'])
    op.create_index('idx_employees_department', 'employees', ['department'])
    op.create_index('idx_renewals_employee_id', 'renewals', ['employee_id'])
    op.create_index('idx_renewals_end_date', 'renewals', ['contract_end_date'])

def downgrade():
    op.drop_index('idx_employees_email', 'employees')
    op.drop_index('idx_employees_department', 'employees')
    op.drop_index('idx_renewals_employee_id', 'renewals')
    op.drop_index('idx_renewals_end_date', 'renewals')