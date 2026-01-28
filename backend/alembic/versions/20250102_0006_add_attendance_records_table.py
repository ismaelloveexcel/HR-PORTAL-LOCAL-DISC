"""Add attendance records table

Revision ID: 20250102_0006
Revises: 20250102_0005
Create Date: 2025-01-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250102_0006'
down_revision = '20250102_0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'attendance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('attendance_date', sa.Date(), nullable=False),
        
        # Clock in/out times
        sa.Column('clock_in', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clock_out', sa.DateTime(timezone=True), nullable=True),
        
        # GPS coordinates for clock in
        sa.Column('clock_in_latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('clock_in_longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('clock_in_address', sa.String(500), nullable=True),
        
        # GPS coordinates for clock out
        sa.Column('clock_out_latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('clock_out_longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('clock_out_address', sa.String(500), nullable=True),
        
        # Work type
        sa.Column('work_type', sa.String(20), nullable=False, server_default='office'),
        
        # WFH specific fields
        sa.Column('wfh_reason', sa.Text(), nullable=True),
        sa.Column('wfh_approved', sa.Boolean(), nullable=True),
        sa.Column('wfh_approved_by', sa.Integer(), nullable=True),
        sa.Column('wfh_approved_at', sa.DateTime(timezone=True), nullable=True),
        
        # Calculated hours
        sa.Column('total_hours', sa.Numeric(5, 2), nullable=True),
        sa.Column('regular_hours', sa.Numeric(5, 2), nullable=True),
        sa.Column('overtime_hours', sa.Numeric(5, 2), nullable=True),
        
        # Overtime tracking
        sa.Column('overtime_type', sa.String(20), nullable=False, server_default='none'),
        sa.Column('overtime_approved', sa.Boolean(), nullable=True),
        sa.Column('overtime_approved_by', sa.Integer(), nullable=True),
        sa.Column('overtime_approved_at', sa.DateTime(timezone=True), nullable=True),
        
        # Break time tracking
        sa.Column('break_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('break_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('break_duration_minutes', sa.Integer(), nullable=True),
        
        # Status
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        
        # Late arrival tracking
        sa.Column('is_late', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('late_minutes', sa.Integer(), nullable=True),
        sa.Column('late_reason', sa.Text(), nullable=True),
        
        # Early departure tracking
        sa.Column('is_early_departure', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('early_departure_minutes', sa.Integer(), nullable=True),
        sa.Column('early_departure_reason', sa.Text(), nullable=True),
        
        # Notes
        sa.Column('notes', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['wfh_approved_by'], ['employees.id']),
        sa.ForeignKeyConstraint(['overtime_approved_by'], ['employees.id']),
    )
    
    # Create indexes
    op.create_index('ix_attendance_records_id', 'attendance_records', ['id'])
    op.create_index('ix_attendance_records_employee_id', 'attendance_records', ['employee_id'])
    op.create_index('ix_attendance_records_attendance_date', 'attendance_records', ['attendance_date'])
    op.create_index('ix_attendance_records_employee_date', 'attendance_records', ['employee_id', 'attendance_date'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_attendance_records_employee_date', table_name='attendance_records')
    op.drop_index('ix_attendance_records_attendance_date', table_name='attendance_records')
    op.drop_index('ix_attendance_records_employee_id', table_name='attendance_records')
    op.drop_index('ix_attendance_records_id', table_name='attendance_records')
    op.drop_table('attendance_records')
