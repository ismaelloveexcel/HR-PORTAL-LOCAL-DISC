"""
Alembic migration for templates table and new indexes.
"""
from alembic import op
import sqlalchemy as sa

revision = '20260103_0007_add_templates_and_indexes'
down_revision = '20260103_0007_add_indexes_for_employee_and_renewal'
branch_labels = None
depends_on = None

def upgrade():
    from sqlalchemy import inspect
    from sqlalchemy import create_engine
    
    op.create_table(
        'templates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('type', sa.String(length=30), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('templates.id'), nullable=True),
        sa.Column('created_by', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('revision_note', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )
    op.create_index('idx_templates_type', 'templates', ['type'])
    op.create_index('idx_templates_name', 'templates', ['name'])
    op.create_index('idx_templates_is_active', 'templates', ['is_active'])
    op.create_index('idx_templates_parent_id', 'templates', ['parent_id'])

def downgrade():
    op.drop_index('idx_templates_parent_id', 'templates')
    op.drop_index('idx_templates_is_active', 'templates')
    op.drop_index('idx_templates_name', 'templates')
    op.drop_index('idx_templates_type', 'templates')
    op.drop_table('templates')
