"""Add onboarding pass stage fields

Revision ID: 20260122_0001
Revises: 20260108_0017_add_pass_feedback_table
Create Date: 2026-01-22 00:50:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260122_0001"
down_revision = "20260108_0017_add_pass_feedback_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("passes", sa.Column("start_stage", sa.String(length=50), nullable=True))
    op.add_column("passes", sa.Column("stage_order", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("passes", "stage_order")
    op.drop_column("passes", "start_stage")
