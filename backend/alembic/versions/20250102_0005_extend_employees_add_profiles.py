"""Extend employees table and add profiles/onboarding tokens.

Revision ID: 20250102_0005
Revises: 20241231_0004
Create Date: 2025-01-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250102_0005'
down_revision: Union[str, None] = '20241231_0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extend employees table with new columns
    op.add_column('employees', sa.Column('job_title', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('function', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('location', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('work_schedule', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('gender', sa.String(20), nullable=True))
    op.add_column('employees', sa.Column('nationality', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('company_phone', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('line_manager_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=True))
    op.add_column('employees', sa.Column('line_manager_name', sa.String(120), nullable=True))
    op.add_column('employees', sa.Column('line_manager_email', sa.String(255), nullable=True))
    op.add_column('employees', sa.Column('joining_date', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('last_promotion_date', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('last_increment_date', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('probation_start_date', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('probation_end_date', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('one_month_eval_date', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('three_month_eval_date', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('six_month_eval_date', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('probation_status', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('employment_status', sa.String(50), nullable=True, server_default='Active'))
    op.add_column('employees', sa.Column('years_of_service', sa.Integer(), nullable=True))
    op.add_column('employees', sa.Column('annual_leave_entitlement', sa.Integer(), nullable=True))
    op.add_column('employees', sa.Column('overtime_type', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('security_clearance', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('visa_status', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('medical_insurance_provider', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('medical_insurance_category', sa.String(100), nullable=True))
    op.add_column('employees', sa.Column('basic_salary', sa.Numeric(12, 2), nullable=True))
    op.add_column('employees', sa.Column('housing_allowance', sa.Numeric(12, 2), nullable=True))
    op.add_column('employees', sa.Column('transportation_allowance', sa.Numeric(12, 2), nullable=True))
    op.add_column('employees', sa.Column('air_ticket_entitlement', sa.Numeric(12, 2), nullable=True))
    op.add_column('employees', sa.Column('other_allowance', sa.Numeric(12, 2), nullable=True))
    op.add_column('employees', sa.Column('consultancy_fees', sa.Numeric(12, 2), nullable=True))
    op.add_column('employees', sa.Column('air_fare_allowance', sa.Numeric(12, 2), nullable=True))
    op.add_column('employees', sa.Column('family_air_ticket_allowance', sa.Numeric(12, 2), nullable=True))
    op.add_column('employees', sa.Column('net_salary', sa.Numeric(12, 2), nullable=True))
    op.add_column('employees', sa.Column('profile_status', sa.String(30), nullable=False, server_default='incomplete'))

    # Create employee_profiles table
    op.create_table(
        'employee_profiles',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('emergency_contact_name', sa.String(120), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(50), nullable=True),
        sa.Column('emergency_contact_relationship', sa.String(50), nullable=True),
        sa.Column('emergency_contact_2_name', sa.String(120), nullable=True),
        sa.Column('emergency_contact_2_phone', sa.String(50), nullable=True),
        sa.Column('emergency_contact_2_relationship', sa.String(50), nullable=True),
        sa.Column('personal_phone', sa.String(50), nullable=True),
        sa.Column('personal_email', sa.String(255), nullable=True),
        sa.Column('current_address', sa.Text(), nullable=True),
        sa.Column('permanent_address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('bank_name', sa.String(100), nullable=True),
        sa.Column('bank_account_number', sa.String(50), nullable=True),
        sa.Column('bank_iban', sa.String(50), nullable=True),
        sa.Column('bank_swift_code', sa.String(20), nullable=True),
        sa.Column('passport_number', sa.String(50), nullable=True),
        sa.Column('passport_expiry', sa.String(20), nullable=True),
        sa.Column('national_id_number', sa.String(50), nullable=True),
        sa.Column('uae_id_number', sa.String(50), nullable=True),
        sa.Column('uae_id_expiry', sa.String(20), nullable=True),
        sa.Column('driving_license_number', sa.String(50), nullable=True),
        sa.Column('driving_license_expiry', sa.String(20), nullable=True),
        sa.Column('driving_license_country', sa.String(100), nullable=True),
        sa.Column('highest_education', sa.String(100), nullable=True),
        sa.Column('education_institution', sa.String(200), nullable=True),
        sa.Column('graduation_year', sa.Integer(), nullable=True),
        sa.Column('shirt_size', sa.String(20), nullable=True),
        sa.Column('pants_size', sa.String(20), nullable=True),
        sa.Column('shoe_size', sa.String(20), nullable=True),
        sa.Column('dietary_restrictions', sa.Text(), nullable=True),
        sa.Column('medical_conditions', sa.Text(), nullable=True),
        sa.Column('additional_notes', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create onboarding_tokens table
    op.create_table(
        'onboarding_tokens',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('is_used', sa.Boolean(), default=False, nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('access_count', sa.Integer(), default=0, nullable=False),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    # Drop new tables
    op.drop_table('onboarding_tokens')
    op.drop_table('employee_profiles')

    # Remove columns from employees table
    op.drop_column('employees', 'profile_status')
    op.drop_column('employees', 'net_salary')
    op.drop_column('employees', 'family_air_ticket_allowance')
    op.drop_column('employees', 'air_fare_allowance')
    op.drop_column('employees', 'consultancy_fees')
    op.drop_column('employees', 'other_allowance')
    op.drop_column('employees', 'air_ticket_entitlement')
    op.drop_column('employees', 'transportation_allowance')
    op.drop_column('employees', 'housing_allowance')
    op.drop_column('employees', 'basic_salary')
    op.drop_column('employees', 'medical_insurance_category')
    op.drop_column('employees', 'medical_insurance_provider')
    op.drop_column('employees', 'visa_status')
    op.drop_column('employees', 'security_clearance')
    op.drop_column('employees', 'overtime_type')
    op.drop_column('employees', 'annual_leave_entitlement')
    op.drop_column('employees', 'years_of_service')
    op.drop_column('employees', 'employment_status')
    op.drop_column('employees', 'probation_status')
    op.drop_column('employees', 'six_month_eval_date')
    op.drop_column('employees', 'three_month_eval_date')
    op.drop_column('employees', 'one_month_eval_date')
    op.drop_column('employees', 'probation_end_date')
    op.drop_column('employees', 'probation_start_date')
    op.drop_column('employees', 'last_increment_date')
    op.drop_column('employees', 'last_promotion_date')
    op.drop_column('employees', 'joining_date')
    op.drop_column('employees', 'line_manager_email')
    op.drop_column('employees', 'line_manager_name')
    op.drop_column('employees', 'line_manager_id')
    op.drop_column('employees', 'company_phone')
    op.drop_column('employees', 'nationality')
    op.drop_column('employees', 'gender')
    op.drop_column('employees', 'work_schedule')
    op.drop_column('employees', 'location')
    op.drop_column('employees', 'function')
    op.drop_column('employees', 'job_title')
