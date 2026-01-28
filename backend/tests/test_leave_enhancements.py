"""Tests for enhanced leave management with UAE 2026 holidays and manager notifications.

Tests coverage:
- UAE 2026 public holidays integration
- Offset days tracking in leave balance
- Manager email notifications
- Enhanced leave calendar with holidays
- Overlap detection and validation
- Balance calculations including offset days
"""
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.leave import LeaveBalance, LeaveRequest
from app.models.public_holiday import PublicHoliday, UAE_HOLIDAYS_2026
from app.services.leave_service import LeaveService


@pytest.fixture
async def test_employee(db_session: AsyncSession):
    """Create a test employee."""
    employee = Employee(
        employee_id="TEST001",
        name="Test Employee",
        email="test.employee@example.com",
        date_of_birth=date(1990, 1, 1),
        password_hash="test_hash",
        role="employee",
        department="IT",
        joining_date=date(2025, 1, 1)
    )
    db_session.add(employee)
    await db_session.commit()
    await db_session.refresh(employee)
    return employee


@pytest.fixture
async def test_manager(db_session: AsyncSession):
    """Create a test manager."""
    manager = Employee(
        employee_id="MGR001",
        name="Test Manager",
        email="test.manager@example.com",
        date_of_birth=date(1985, 1, 1),
        password_hash="test_hash",
        role="manager",
        department="IT",
        joining_date=date(2020, 1, 1)
    )
    db_session.add(manager)
    await db_session.commit()
    await db_session.refresh(manager)
    return manager


@pytest.fixture
async def test_leave_balance(db_session: AsyncSession, test_employee: Employee):
    """Create a test leave balance."""
    balance = LeaveBalance(
        employee_id=test_employee.id,
        year=2026,
        leave_type="annual",
        entitlement=Decimal("30"),
        carried_forward=Decimal("5"),
        used=Decimal("0"),
        pending=Decimal("0"),
        offset_days_used=Decimal("0")
    )
    db_session.add(balance)
    await db_session.commit()
    await db_session.refresh(balance)
    return balance


@pytest.fixture
async def uae_2026_holidays(db_session: AsyncSession):
    """Seed UAE 2026 public holidays."""
    holidays = []
    for holiday_data in UAE_HOLIDAYS_2026:
        holiday = PublicHoliday(
            name=holiday_data["name"],
            name_arabic=holiday_data["name_arabic"],
            start_date=holiday_data["start_date"],
            end_date=holiday_data["end_date"],
            year=holiday_data["year"],
            holiday_type=holiday_data["holiday_type"],
            is_paid=holiday_data["is_paid"],
            description=holiday_data["description"],
            is_active=True
        )
        db_session.add(holiday)
        holidays.append(holiday)
    
    await db_session.commit()
    return holidays


class TestUAE2026Holidays:
    """Test UAE 2026 public holidays integration."""
    
    async def test_uae_2026_holidays_count(self, uae_2026_holidays):
        """Test that all 8 UAE 2026 official holidays are loaded."""
        assert len(uae_2026_holidays) == 8
    
    async def test_new_year_holiday(self, uae_2026_holidays):
        """Test New Year's Day holiday."""
        new_year = next(h for h in uae_2026_holidays if "New Year" in h.name)
        assert new_year.start_date == date(2026, 1, 1)
        assert new_year.is_paid is True
        assert new_year.holiday_type == "uae_official"
    
    async def test_national_day_holiday(self, uae_2026_holidays):
        """Test UAE National Day holiday (multi-day)."""
        national_day = next(h for h in uae_2026_holidays if "National Day" in h.name)
        assert national_day.start_date == date(2026, 12, 2)
        assert national_day.end_date == date(2026, 12, 3)
        assert (national_day.end_date - national_day.start_date).days == 1
    
    async def test_eid_holidays_present(self, uae_2026_holidays):
        """Test that both Eid holidays are present."""
        eid_fitr = next((h for h in uae_2026_holidays if "Fitr" in h.name), None)
        eid_adha = next((h for h in uae_2026_holidays if "Adha" in h.name), None)
        
        assert eid_fitr is not None
        assert eid_adha is not None
        assert eid_fitr.is_paid is True
        assert eid_adha.is_paid is True


class TestLeaveBalanceWithOffset:
    """Test leave balance calculations with offset days."""
    
    async def test_offset_days_in_balance(self, test_leave_balance):
        """Test that offset_days_used is tracked in balance."""
        assert hasattr(test_leave_balance, 'offset_days_used')
        assert test_leave_balance.offset_days_used == Decimal("0")
    
    async def test_available_balance_calculation(self, test_leave_balance):
        """Test available balance calculation includes all components."""
        # Available = Entitlement + Carried Forward + Adjustment - Used - Pending
        # 30 + 5 + 0 - 0 - 0 = 35
        assert test_leave_balance.available == Decimal("35")
    
    async def test_balance_with_offset_used(self, db_session: AsyncSession, test_leave_balance):
        """Test balance calculation when offset days are used."""
        test_leave_balance.offset_days_used = Decimal("2")
        test_leave_balance.used = Decimal("3")
        await db_session.commit()
        await db_session.refresh(test_leave_balance)
        
        # Available = 30 + 5 + 0 - 3 - 0 = 32
        # (offset_days_used is tracked separately, doesn't affect available directly)
        assert test_leave_balance.available == Decimal("32")


class TestManagerNotifications:
    """Test manager notification functionality."""
    
    async def test_manager_email_stored_on_request(
        self, 
        db_session: AsyncSession,
        test_employee: Employee,
        test_manager: Employee
    ):
        """Test that manager email is stored when leave request is created."""
        # Set manager for employee
        test_employee.line_manager_id = test_manager.id
        test_employee.line_manager_email = test_manager.email
        await db_session.commit()
        
        # Create leave request
        leave_request = LeaveRequest(
            employee_id=test_employee.id,
            leave_type="annual",
            start_date=date(2026, 2, 10),
            end_date=date(2026, 2, 14),
            total_days=Decimal("5"),
            status="pending",
            manager_email=test_manager.email,
            overlaps_checked=True
        )
        db_session.add(leave_request)
        await db_session.commit()
        await db_session.refresh(leave_request)
        
        assert leave_request.manager_email == test_manager.email
        assert leave_request.manager_notified is False
    
    @patch('app.services.leave_service.get_email_service')
    async def test_send_manager_notification(
        self,
        mock_email_service,
        db_session: AsyncSession,
        test_employee: Employee,
        test_manager: Employee,
        test_leave_balance: LeaveBalance
    ):
        """Test sending email notification to manager."""
        # Mock email service
        mock_email = AsyncMock()
        mock_email.send_email = AsyncMock(return_value=True)
        mock_email_service.return_value = mock_email
        
        # Create leave request
        leave_request = LeaveRequest(
            employee_id=test_employee.id,
            leave_type="annual",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 5),
            total_days=Decimal("5"),
            status="pending",
            manager_email=test_manager.email
        )
        db_session.add(leave_request)
        await db_session.commit()
        await db_session.refresh(leave_request)
        
        # Send notification
        leave_service = LeaveService(db_session)
        success = await leave_service.send_manager_notification(
            leave_request, test_employee, test_manager
        )
        
        assert success is True
        assert leave_request.manager_notified is True
        assert leave_request.notification_sent_at is not None


class TestOverlapDetection:
    """Test leave overlap detection and validation."""
    
    async def test_no_overlap_when_dates_different(
        self,
        db_session: AsyncSession,
        test_employee: Employee
    ):
        """Test that non-overlapping dates pass validation."""
        # Create first leave request
        leave1 = LeaveRequest(
            employee_id=test_employee.id,
            leave_type="annual",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 5),
            total_days=Decimal("5"),
            status="approved",
            overlaps_checked=True
        )
        db_session.add(leave1)
        await db_session.commit()
        
        # Check for overlap with different dates
        leave_service = LeaveService(db_session)
        overlap = await leave_service.check_overlapping_leaves(
            employee_id=test_employee.id,
            start_date=date(2026, 2, 10),
            end_date=date(2026, 2, 15)
        )
        
        assert overlap is None
    
    async def test_overlap_detected(
        self,
        db_session: AsyncSession,
        test_employee: Employee
    ):
        """Test that overlapping dates are detected."""
        # Create first leave request
        leave1 = LeaveRequest(
            employee_id=test_employee.id,
            leave_type="annual",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 10),
            total_days=Decimal("10"),
            status="approved",
            overlaps_checked=True
        )
        db_session.add(leave1)
        await db_session.commit()
        
        # Check for overlap with overlapping dates
        leave_service = LeaveService(db_session)
        overlap = await leave_service.check_overlapping_leaves(
            employee_id=test_employee.id,
            start_date=date(2026, 3, 5),
            end_date=date(2026, 3, 15)
        )
        
        assert overlap is not None
        assert overlap.id == leave1.id
    
    async def test_overlaps_checked_flag(
        self,
        db_session: AsyncSession,
        test_employee: Employee
    ):
        """Test that overlaps_checked flag is set."""
        leave_request = LeaveRequest(
            employee_id=test_employee.id,
            leave_type="annual",
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 5),
            total_days=Decimal("5"),
            status="pending",
            overlaps_checked=True
        )
        db_session.add(leave_request)
        await db_session.commit()
        await db_session.refresh(leave_request)
        
        assert leave_request.overlaps_checked is True


class TestLeaveCalendarWithHolidays:
    """Test leave calendar integration with public holidays."""
    
    async def test_calculate_working_days_excluding_holidays(
        self,
        db_session: AsyncSession,
        uae_2026_holidays
    ):
        """Test working days calculation excludes public holidays."""
        leave_service = LeaveService(db_session)
        
        # Calculate days for a period that includes New Year (Jan 1)
        working_days = await leave_service.calculate_working_days(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 5),
            exclude_holidays=True
        )
        
        # Total: 5 days, minus 1 holiday (Jan 1) = 4 working days
        assert working_days == Decimal("4")
    
    async def test_calculate_days_without_excluding_holidays(
        self,
        db_session: AsyncSession,
        uae_2026_holidays
    ):
        """Test day calculation without excluding holidays."""
        leave_service = LeaveService(db_session)
        
        days = await leave_service.calculate_working_days(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 5),
            exclude_holidays=False
        )
        
        # Should be 5 days regardless of holidays
        assert days == Decimal("5")
    
    async def test_get_holidays_in_range(
        self,
        db_session: AsyncSession,
        uae_2026_holidays
    ):
        """Test retrieving holidays within a date range."""
        leave_service = LeaveService(db_session)
        
        # Get holidays in January 2026
        holidays = await leave_service.get_public_holidays_in_range(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31)
        )
        
        # Should get New Year's Day
        assert len(holidays) == 1
        assert holidays[0].name == "New Year's Day"


class TestLeaveValidation:
    """Test comprehensive leave validation."""
    
    async def test_validate_leave_request_success(
        self,
        db_session: AsyncSession,
        test_employee: Employee,
        test_leave_balance: LeaveBalance
    ):
        """Test successful leave request validation."""
        leave_service = LeaveService(db_session)
        
        is_valid, error_msg, days = await leave_service.validate_leave_request(
            employee_id=test_employee.id,
            leave_type="annual",
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 5),
            is_half_day=False
        )
        
        assert is_valid is True
        assert error_msg is None
        assert days == Decimal("5")
    
    async def test_validate_insufficient_balance(
        self,
        db_session: AsyncSession,
        test_employee: Employee
    ):
        """Test validation fails with insufficient balance."""
        # Create balance with low entitlement
        balance = LeaveBalance(
            employee_id=test_employee.id,
            year=2026,
            leave_type="annual",
            entitlement=Decimal("2"),
            carried_forward=Decimal("0"),
            used=Decimal("0"),
            pending=Decimal("0")
        )
        db_session.add(balance)
        await db_session.commit()
        
        leave_service = LeaveService(db_session)
        
        is_valid, error_msg, days = await leave_service.validate_leave_request(
            employee_id=test_employee.id,
            leave_type="annual",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 10),
            is_half_day=False
        )
        
        assert is_valid is False
        assert "Insufficient balance" in error_msg
    
    async def test_validate_half_day_leave(
        self,
        db_session: AsyncSession,
        test_employee: Employee,
        test_leave_balance: LeaveBalance
    ):
        """Test half-day leave validation."""
        leave_service = LeaveService(db_session)
        
        is_valid, error_msg, days = await leave_service.validate_leave_request(
            employee_id=test_employee.id,
            leave_type="annual",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 1),
            is_half_day=True
        )
        
        assert is_valid is True
        assert days == Decimal("0.5")


class TestUAEComplianceArticle29:
    """Test UAE compliance for Article 29 (Annual Leave)."""
    
    async def test_annual_leave_entitlement_30_days(self, test_leave_balance):
        """Test that annual leave entitlement is 30 days (Article 29)."""
        assert test_leave_balance.leave_type == "annual"
        assert test_leave_balance.entitlement == Decimal("30")
    
    async def test_carried_forward_support(self, test_leave_balance):
        """Test that carry-forward from previous year is supported."""
        assert test_leave_balance.carried_forward == Decimal("5")
        # Available includes carried forward
        assert test_leave_balance.available >= test_leave_balance.carried_forward
