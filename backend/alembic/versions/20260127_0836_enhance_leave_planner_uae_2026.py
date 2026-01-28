"""Enhance leave planner with UAE 2026 holidays, offset tracking, and manager notifications

Revision ID: 20260127_0836
Revises: 20260122_0001
Create Date: 2026-01-27 08:36:00.000000

This migration enhances the leave management system with:
1. UAE 2026 public holidays seed data (8 official holidays, 14 total days)
2. Offset days tracking in leave_balances table
3. Manager notification fields in leave_requests table
4. Validation flags for overlap checking

UAE Compliance:
- Article 29: Annual leave entitlement and carry-forward provisions
- Cabinet Resolution No. 1 of 2022: Public holidays (8 holidays minimum)
- Federal Decree-Law No. 33 of 2021: Leave management requirements
"""
from alembic import op
import sqlalchemy as sa
from datetime import date

# revision identifiers, used by Alembic.
revision = '20260127_0836'
down_revision = '20260122_0001'
branch_labels = None
depends_on = None


def upgrade():
    """Add enhanced leave planner fields and UAE 2026 holidays."""
    
    # 1. Add offset_days_used to leave_balances table
    op.add_column('leave_balances', 
        sa.Column('offset_days_used', sa.Numeric(5, 2), nullable=False, server_default='0')
    )
    
    # 2. Add manager notification fields to leave_requests table
    op.add_column('leave_requests',
        sa.Column('manager_email', sa.String(255), nullable=True)
    )
    op.add_column('leave_requests',
        sa.Column('manager_notified', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column('leave_requests',
        sa.Column('notification_sent_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # 3. Add validation flags to leave_requests table
    op.add_column('leave_requests',
        sa.Column('overlaps_checked', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # 4. Add indexes for performance
    op.create_index('ix_leave_requests_manager_email', 'leave_requests', ['manager_email'])
    op.create_index('ix_leave_requests_manager_notified', 'leave_requests', ['manager_notified'])
    
    # 5. Seed UAE 2026 public holidays
    # Connect to the database
    connection = op.get_bind()
    
    # Check if holidays already exist for 2026
    result = connection.execute(
        sa.text("SELECT COUNT(*) FROM public_holidays WHERE year = 2026")
    )
    count = result.scalar()
    
    # Only insert if no 2026 holidays exist
    if count == 0:
        # UAE 2026 Official Public Holidays
        holidays_2026 = [
            {
                "name": "New Year's Day",
                "name_arabic": "رأس السنة الميلادية",
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 1, 1),
                "year": 2026,
                "holiday_type": "uae_official",
                "is_paid": True,
                "description": "New Year's Day - January 1",
                "is_active": True
            },
            {
                "name": "Eid Al Fitr",
                "name_arabic": "عيد الفطر",
                "start_date": date(2026, 3, 20),
                "end_date": date(2026, 3, 23),
                "year": 2026,
                "holiday_type": "uae_official",
                "is_paid": True,
                "description": "Eid Al Fitr - 4 days (approximate, subject to moon sighting)",
                "is_active": True
            },
            {
                "name": "Arafat Day",
                "name_arabic": "يوم عرفة",
                "start_date": date(2026, 5, 26),
                "end_date": date(2026, 5, 26),
                "year": 2026,
                "holiday_type": "uae_official",
                "is_paid": True,
                "description": "Arafat Day - Day before Eid Al Adha (approximate)",
                "is_active": True
            },
            {
                "name": "Eid Al Adha",
                "name_arabic": "عيد الأضحى",
                "start_date": date(2026, 5, 27),
                "end_date": date(2026, 5, 29),
                "year": 2026,
                "holiday_type": "uae_official",
                "is_paid": True,
                "description": "Eid Al Adha - 3 days (approximate, subject to moon sighting)",
                "is_active": True
            },
            {
                "name": "Islamic New Year",
                "name_arabic": "رأس السنة الهجرية",
                "start_date": date(2026, 6, 16),
                "end_date": date(2026, 6, 16),
                "year": 2026,
                "holiday_type": "uae_official",
                "is_paid": True,
                "description": "Hijri New Year 1448 (approximate)",
                "is_active": True
            },
            {
                "name": "Prophet's Birthday",
                "name_arabic": "المولد النبوي الشريف",
                "start_date": date(2026, 8, 25),
                "end_date": date(2026, 8, 25),
                "year": 2026,
                "holiday_type": "uae_official",
                "is_paid": True,
                "description": "Mawlid Al Nabi - Prophet Muhammad's Birthday (approximate)",
                "is_active": True
            },
            {
                "name": "Commemoration Day",
                "name_arabic": "يوم الشهيد",
                "start_date": date(2026, 11, 30),
                "end_date": date(2026, 11, 30),
                "year": 2026,
                "holiday_type": "uae_official",
                "is_paid": True,
                "description": "Martyrs' Day - November 30",
                "is_active": True
            },
            {
                "name": "UAE National Day",
                "name_arabic": "اليوم الوطني لدولة الإمارات",
                "start_date": date(2026, 12, 2),
                "end_date": date(2026, 12, 3),
                "year": 2026,
                "holiday_type": "uae_official",
                "is_paid": True,
                "description": "UAE National Day - December 2-3 (48th & 49th Anniversary)",
                "is_active": True
            }
        ]
        
        # Insert holidays
        for holiday in holidays_2026:
            connection.execute(
                sa.text("""
                    INSERT INTO public_holidays 
                    (name, name_arabic, start_date, end_date, year, holiday_type, is_paid, description, is_active, created_at, updated_at)
                    VALUES 
                    (:name, :name_arabic, :start_date, :end_date, :year, :holiday_type, :is_paid, :description, :is_active, NOW(), NOW())
                """),
                {
                    "name": holiday["name"],
                    "name_arabic": holiday["name_arabic"],
                    "start_date": holiday["start_date"],
                    "end_date": holiday["end_date"],
                    "year": holiday["year"],
                    "holiday_type": holiday["holiday_type"],
                    "is_paid": holiday["is_paid"],
                    "description": holiday["description"],
                    "is_active": holiday["is_active"]
                }
            )
        
        print(f"✅ Seeded {len(holidays_2026)} UAE 2026 public holidays")


def downgrade():
    """Remove enhanced leave planner fields and UAE 2026 holidays."""
    
    # Remove indexes
    op.drop_index('ix_leave_requests_manager_notified', 'leave_requests')
    op.drop_index('ix_leave_requests_manager_email', 'leave_requests')
    
    # Remove columns from leave_requests
    op.drop_column('leave_requests', 'overlaps_checked')
    op.drop_column('leave_requests', 'notification_sent_at')
    op.drop_column('leave_requests', 'manager_notified')
    op.drop_column('leave_requests', 'manager_email')
    
    # Remove column from leave_balances
    op.drop_column('leave_balances', 'offset_days_used')
    
    # Remove UAE 2026 holidays
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM public_holidays WHERE year = 2026 AND holiday_type = 'uae_official'")
    )
    
    print("⚠️  Rolled back leave planner enhancements and removed UAE 2026 holidays")
