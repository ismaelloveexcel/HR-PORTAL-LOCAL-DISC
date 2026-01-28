"""add_offer_tracking_and_reminder_fields

Revision ID: 20260127_1200
Revises: 20260127_0836
Create Date: 2026-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260127_1200'
down_revision: Union[str, None] = '20260127_0836'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add offer tracking fields to candidates table
    op.add_column('candidates', sa.Column('offer_letter_sent', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('candidates', sa.Column('offer_details', sa.JSON(), nullable=True))
    op.add_column('candidates', sa.Column('offer_accepted', sa.Boolean(), nullable=True))
    
    # Add reminder fields to performance_reviews table
    op.add_column('performance_reviews', sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('performance_reviews', sa.Column('reminder_sent_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove reminder fields from performance_reviews table
    op.drop_column('performance_reviews', 'reminder_sent_at')
    op.drop_column('performance_reviews', 'reminder_sent')
    
    # Remove offer tracking fields from candidates table
    op.drop_column('candidates', 'offer_accepted')
    op.drop_column('candidates', 'offer_details')
    op.drop_column('candidates', 'offer_letter_sent')
