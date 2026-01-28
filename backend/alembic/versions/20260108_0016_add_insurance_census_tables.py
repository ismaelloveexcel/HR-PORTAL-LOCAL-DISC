"""add insurance census tables

Revision ID: 0016
Revises: 0015
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision = '20260108_0016'
down_revision = '20260108_0015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'insurance_census_records',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('entity', sa.String(50), nullable=False),
        sa.Column('insurance_type', sa.String(20), nullable=False),
        sa.Column('employee_id', sa.Integer(), sa.ForeignKey('employees.id', ondelete='SET NULL'), nullable=True),
        sa.Column('sr_no', sa.String(20), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('second_name', sa.String(100), nullable=True),
        sa.Column('family_name', sa.String(100), nullable=True),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('dob', sa.String(50), nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('marital_status', sa.String(50), nullable=True),
        sa.Column('maternity_coverage', sa.String(20), nullable=True),
        sa.Column('relation', sa.String(50), nullable=True),
        sa.Column('staff_id', sa.String(50), nullable=True, index=True),
        sa.Column('employee_card_number', sa.String(50), nullable=True),
        sa.Column('category', sa.String(255), nullable=True),
        sa.Column('sub_group_name', sa.String(255), nullable=True),
        sa.Column('billing_entity', sa.String(255), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('nationality', sa.String(100), nullable=True),
        sa.Column('effective_date', sa.String(50), nullable=True),
        sa.Column('emirates_id_number', sa.String(50), nullable=True),
        sa.Column('emirates_id_application_number', sa.String(100), nullable=True),
        sa.Column('emirates_id_processing_note', sa.Text(), nullable=True),
        sa.Column('birth_notification_no', sa.String(100), nullable=True),
        sa.Column('uid_number', sa.String(50), nullable=True),
        sa.Column('gdrfa_file_number', sa.String(100), nullable=True),
        sa.Column('country_of_residency', sa.String(100), nullable=True),
        sa.Column('member_type', sa.String(50), nullable=True),
        sa.Column('occupation', sa.String(100), nullable=True),
        sa.Column('emirate_of_residency', sa.String(50), nullable=True),
        sa.Column('residency_location', sa.String(100), nullable=True),
        sa.Column('emirate_of_work', sa.String(50), nullable=True),
        sa.Column('work_location', sa.String(100), nullable=True),
        sa.Column('emirate_of_visa', sa.String(50), nullable=True),
        sa.Column('passport_number', sa.String(50), nullable=True),
        sa.Column('salary', sa.String(50), nullable=True),
        sa.Column('commission', sa.String(50), nullable=True),
        sa.Column('establishment_type', sa.String(100), nullable=True),
        sa.Column('entity_id', sa.String(50), nullable=True),
        sa.Column('company_phone', sa.String(50), nullable=True),
        sa.Column('company_email', sa.String(100), nullable=True),
        sa.Column('landline_no', sa.String(50), nullable=True),
        sa.Column('mobile_no', sa.String(50), nullable=True),
        sa.Column('personal_email', sa.String(100), nullable=True),
        sa.Column('vip', sa.String(20), nullable=True),
        sa.Column('height', sa.String(20), nullable=True),
        sa.Column('weight', sa.String(20), nullable=True),
        sa.Column('missing_fields', JSON, nullable=True),
        sa.Column('completeness_pct', sa.Integer(), nullable=True, default=0),
        sa.Column('import_batch_id', sa.String(50), nullable=True),
        sa.Column('import_filename', sa.String(255), nullable=True),
        sa.Column('imported_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('updated_by', sa.String(50), nullable=True),
    )
    
    op.create_table(
        'insurance_census_import_batches',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('batch_id', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('entity', sa.String(50), nullable=False),
        sa.Column('insurance_type', sa.String(20), nullable=False),
        sa.Column('total_records', sa.Integer(), default=0),
        sa.Column('linked_records', sa.Integer(), default=0),
        sa.Column('unlinked_records', sa.Integer(), default=0),
        sa.Column('imported_by', sa.String(50), nullable=True),
        sa.Column('imported_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('notes', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('insurance_census_import_batches')
    op.drop_table('insurance_census_records')
