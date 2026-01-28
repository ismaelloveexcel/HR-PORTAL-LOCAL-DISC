"""Add nomination_settings table

Revision ID: 20260116_0023
Revises: 20260110_0020_backfill_line_manager_id
Create Date: 2026-01-16

"""
from alembic import op
import sqlalchemy as sa

revision = '20260116_0023'
down_revision = '20260110_0021'
branch_labels = None
depends_on = None


def upgrade():
    # Create nomination_settings table if it doesn't exist
    op.create_table(
        'nomination_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('is_open', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('announcement_message', sa.Text(), nullable=True),
        sa.Column('invitation_email_subject', sa.String(255), nullable=True),
        sa.Column('invitation_email_body', sa.Text(), nullable=True),
        sa.Column('last_email_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('emails_sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('year', name='uq_nomination_settings_year')
    )
    op.create_index('ix_nomination_settings_id', 'nomination_settings', ['id'])
    op.create_index('ix_nomination_settings_year', 'nomination_settings', ['year'])


def downgrade():
    op.drop_index('ix_nomination_settings_year', table_name='nomination_settings')
    op.drop_index('ix_nomination_settings_id', table_name='nomination_settings')
    op.drop_table('nomination_settings')
