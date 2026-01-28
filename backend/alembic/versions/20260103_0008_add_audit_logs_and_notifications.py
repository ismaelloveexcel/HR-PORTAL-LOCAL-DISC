"""
Alembic migration for audit_logs and notifications tables.
"""
from alembic import op
import sqlalchemy as sa

revision = '20260103_0008_add_audit_logs_and_notifications'
down_revision = '20260103_0007_add_templates_and_indexes'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(length=50), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
    )
    op.create_index('idx_audit_logs_entity', 'audit_logs', ['entity'])
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_timestamp', 'audit_logs', ['timestamp'])

    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(length=50), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('type', sa.String(length=30), nullable=True),
        sa.Column('link', sa.String(length=255), nullable=True),
    )
    op.create_index('idx_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('idx_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('idx_notifications_created_at', 'notifications', ['created_at'])

def downgrade():
    op.drop_index('idx_notifications_created_at', 'notifications')
    op.drop_index('idx_notifications_is_read', 'notifications')
    op.drop_index('idx_notifications_user_id', 'notifications')
    op.drop_table('notifications')
    op.drop_index('idx_audit_logs_timestamp', 'audit_logs')
    op.drop_index('idx_audit_logs_user_id', 'audit_logs')
    op.drop_index('idx_audit_logs_entity', 'audit_logs')
    op.drop_table('audit_logs')
