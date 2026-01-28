"""Add performance management tables

Revision ID: 20260107_0011
Revises: 20260106_0010
Create Date: 2026-01-07

"""
from alembic import op
import sqlalchemy as sa


revision = '20260107_0011'
down_revision = '20260106_0010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'performance_cycles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('cycle_type', sa.String(50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('self_assessment_deadline', sa.Date(), nullable=True),
        sa.Column('manager_review_deadline', sa.Date(), nullable=True),
        sa.Column('status', sa.String(30), server_default='draft', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_performance_cycles_status', 'performance_cycles', ['status'])

    op.create_table(
        'performance_reviews',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cycle_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(30), server_default='pending', nullable=False),
        sa.Column('self_assessment_submitted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('self_assessment_date', sa.DateTime(), nullable=True),
        sa.Column('self_achievements', sa.Text(), nullable=True),
        sa.Column('self_challenges', sa.Text(), nullable=True),
        sa.Column('self_goals_next_period', sa.Text(), nullable=True),
        sa.Column('self_training_needs', sa.Text(), nullable=True),
        sa.Column('self_overall_comments', sa.Text(), nullable=True),
        sa.Column('manager_review_submitted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('manager_review_date', sa.DateTime(), nullable=True),
        sa.Column('manager_achievements', sa.Text(), nullable=True),
        sa.Column('manager_areas_improvement', sa.Text(), nullable=True),
        sa.Column('manager_recommendations', sa.Text(), nullable=True),
        sa.Column('manager_overall_comments', sa.Text(), nullable=True),
        sa.Column('overall_rating', sa.Numeric(3, 2), nullable=True),
        sa.Column('rating_label', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cycle_id'], ['performance_cycles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['employees.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_performance_reviews_cycle_id', 'performance_reviews', ['cycle_id'])
    op.create_index('ix_performance_reviews_employee_id', 'performance_reviews', ['employee_id'])
    op.create_index('ix_performance_reviews_status', 'performance_reviews', ['status'])

    op.create_table(
        'performance_ratings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('competency_name', sa.String(100), nullable=False),
        sa.Column('competency_category', sa.String(50), nullable=False),
        sa.Column('weight', sa.Integer(), server_default='0', nullable=False),
        sa.Column('self_rating', sa.Integer(), nullable=True),
        sa.Column('self_comments', sa.Text(), nullable=True),
        sa.Column('manager_rating', sa.Integer(), nullable=True),
        sa.Column('manager_comments', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['review_id'], ['performance_reviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_performance_ratings_review_id', 'performance_ratings', ['review_id'])


def downgrade() -> None:
    op.drop_index('ix_performance_ratings_review_id')
    op.drop_table('performance_ratings')
    op.drop_index('ix_performance_reviews_status')
    op.drop_index('ix_performance_reviews_employee_id')
    op.drop_index('ix_performance_reviews_cycle_id')
    op.drop_table('performance_reviews')
    op.drop_index('ix_performance_cycles_status')
    op.drop_table('performance_cycles')
