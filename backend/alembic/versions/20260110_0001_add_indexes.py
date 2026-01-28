"""Add database indexes for performance

Revision ID: 20260110_0021
Revises: 20260110_0020
Create Date: 2026-01-10

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '20260110_0021'
down_revision = '20260110_0020'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Employees table indexes
    op.create_index('idx_employees_employee_id', 'employees', ['employee_id'], unique=False, if_not_exists=True)
    op.create_index('idx_employees_department', 'employees', ['department'], unique=False, if_not_exists=True)
    op.create_index('idx_employees_is_active', 'employees', ['is_active'], unique=False, if_not_exists=True)
    op.create_index('idx_employees_profile_status', 'employees', ['profile_status'], unique=False, if_not_exists=True)
    op.create_index('idx_employees_created_at', 'employees', ['created_at'], unique=False, if_not_exists=True, postgresql_ops={'created_at': 'DESC'})
    
    # Composite index
    op.create_index('idx_employees_active_department', 'employees', ['is_active', 'department'], unique=False, if_not_exists=True)
    
    # Compliance expiry indexes (partial indexes)
    op.execute('CREATE INDEX IF NOT EXISTS idx_employees_visa_expiry ON employees(visa_expiry_date) WHERE visa_expiry_date IS NOT NULL')
    op.execute('CREATE INDEX IF NOT EXISTS idx_employees_emirates_id_expiry ON employees(emirates_id_expiry) WHERE emirates_id_expiry IS NOT NULL')
    op.execute('CREATE INDEX IF NOT EXISTS idx_employees_medical_expiry ON employees(medical_fitness_expiry) WHERE medical_fitness_expiry IS NOT NULL')
    op.execute('CREATE INDEX IF NOT EXISTS idx_employees_contract_expiry ON employees(contract_end_date) WHERE contract_end_date IS NOT NULL')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_employees_contract_expiry', if_exists=True)
    op.drop_index('idx_employees_medical_expiry', if_exists=True)
    op.drop_index('idx_employees_emirates_id_expiry', if_exists=True)
    op.drop_index('idx_employees_visa_expiry', if_exists=True)
    op.drop_index('idx_employees_active_department', if_exists=True)
    op.drop_index('idx_employees_created_at', if_exists=True)
    op.drop_index('idx_employees_profile_status', if_exists=True)
    op.drop_index('idx_employees_is_active', if_exists=True)
    op.drop_index('idx_employees_department', if_exists=True)
    op.drop_index('idx_employees_employee_id', if_exists=True)
