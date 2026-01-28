"""Add leave, public_holidays, timesheet, and geofence tables

Revision ID: 20260109_0022
Revises: 20260109_0021
Create Date: 2026-01-09

This migration adds tables for:
1. leave_balances - Employee leave entitlements and usage
2. leave_requests - Leave request workflow
3. public_holidays - UAE and company holidays
4. timesheets - Monthly timesheet summary
5. geofences - Location-based attendance validation
"""
from alembic import op
import sqlalchemy as sa


revision = '20260109_0022'
down_revision = '20260109_0021'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Leave Balances table
    op.create_table('leave_balances',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=False, index=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('leave_type', sa.String(50), nullable=False),
        sa.Column('entitlement', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('carried_forward', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('used', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('pending', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('adjustment', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('adjustment_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Leave Requests table
    op.create_table('leave_requests',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=False, index=True),
        sa.Column('leave_type', sa.String(50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False, index=True),
        sa.Column('end_date', sa.Date(), nullable=False, index=True),
        sa.Column('is_half_day', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('half_day_type', sa.String(20), nullable=True),
        sa.Column('total_days', sa.Numeric(5, 2), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('document_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('approved_by', sa.Integer(), sa.ForeignKey('employees.id'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('emergency_contact', sa.String(200), nullable=True),
        sa.Column('emergency_phone', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Public Holidays table
    op.create_table('public_holidays',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('name_arabic', sa.String(200), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False, index=True),
        sa.Column('end_date', sa.Date(), nullable=False, index=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('holiday_type', sa.String(50), nullable=False),
        sa.Column('is_paid', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Timesheets table
    op.create_table('timesheets',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id'), nullable=False, index=True),
        sa.Column('year', sa.Integer(), nullable=False, index=True),
        sa.Column('month', sa.Integer(), nullable=False, index=True),
        # Attendance counts
        sa.Column('total_working_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_present_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_absent_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_leave_days', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('total_wfh_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_late_arrivals', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_early_departures', sa.Integer(), nullable=False, server_default='0'),
        # Hours
        sa.Column('total_regular_hours', sa.Numeric(7, 2), nullable=False, server_default='0'),
        sa.Column('total_overtime_hours', sa.Numeric(6, 2), nullable=False, server_default='0'),
        sa.Column('total_night_overtime_hours', sa.Numeric(6, 2), nullable=False, server_default='0'),
        sa.Column('total_holiday_overtime_hours', sa.Numeric(6, 2), nullable=False, server_default='0'),
        sa.Column('total_overtime_amount', sa.Numeric(10, 2), nullable=False, server_default='0'),
        # Offset
        sa.Column('offset_hours_earned', sa.Numeric(6, 2), nullable=False, server_default='0'),
        sa.Column('offset_hours_used', sa.Numeric(6, 2), nullable=False, server_default='0'),
        # Location breakdown
        sa.Column('days_at_head_office', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_at_kezad', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_at_safario', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_at_sites', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_at_meeting', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('days_at_event', sa.Integer(), nullable=False, server_default='0'),
        # Food allowance
        sa.Column('food_allowance_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('food_allowance_total', sa.Numeric(10, 2), nullable=False, server_default='0'),
        # Compliance
        sa.Column('has_compliance_issues', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('compliance_notes', sa.Text(), nullable=True),
        # Status
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        # Employee submission
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('employee_notes', sa.Text(), nullable=True),
        # Manager approval
        sa.Column('manager_approved_by', sa.Integer(), sa.ForeignKey('employees.id'), nullable=True),
        sa.Column('manager_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('manager_notes', sa.Text(), nullable=True),
        # HR approval
        sa.Column('hr_approved_by', sa.Integer(), sa.ForeignKey('employees.id'), nullable=True),
        sa.Column('hr_approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('hr_notes', sa.Text(), nullable=True),
        # Rejection
        sa.Column('rejected_by', sa.Integer(), sa.ForeignKey('employees.id'), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        # Payroll
        sa.Column('exported_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payroll_reference', sa.String(100), nullable=True),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Geofences table
    op.create_table('geofences',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=False),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=False),
        sa.Column('radius_meters', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('validation_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    
    # Add indexes for common queries
    op.create_index('ix_leave_balances_emp_year', 'leave_balances', ['employee_id', 'year'])
    op.create_index('ix_leave_requests_dates', 'leave_requests', ['start_date', 'end_date'])
    op.create_index('ix_timesheets_emp_period', 'timesheets', ['employee_id', 'year', 'month'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_timesheets_emp_period')
    op.drop_index('ix_leave_requests_dates')
    op.drop_index('ix_leave_balances_emp_year')
    op.drop_table('geofences')
    op.drop_table('timesheets')
    op.drop_table('public_holidays')
    op.drop_table('leave_requests')
    op.drop_table('leave_balances')
