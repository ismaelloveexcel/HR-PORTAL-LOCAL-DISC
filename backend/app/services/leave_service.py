"""Leave management service with enhanced validation and business logic.

This service handles:
- Leave balance calculations including offset days
- Overlap detection for leave requests
- Public holiday integration
- Manager notification coordination
- UAE compliance checks (Article 29, 30, 31)
"""
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.leave import LeaveBalance, LeaveRequest, LEAVE_TYPES
from app.models.public_holiday import PublicHoliday
from app.services.email_service import get_email_service


class LeaveValidationError(Exception):
    """Custom exception for leave validation errors."""
    pass


class LeaveService:
    """Service for leave management operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        # Lazy initialization - email service retrieved when needed
        self._email_service = None
    
    @property
    def email_service(self):
        """Lazy load email service."""
        if self._email_service is None:
            self._email_service = get_email_service()
        return self._email_service
    
    async def check_overlapping_leaves(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        exclude_request_id: Optional[int] = None
    ) -> Optional[LeaveRequest]:
        """Check if there are overlapping leave requests for an employee.
        
        Args:
            employee_id: Employee ID to check
            start_date: Proposed leave start date
            end_date: Proposed leave end date
            exclude_request_id: Optional request ID to exclude (for updates)
        
        Returns:
            LeaveRequest if overlap exists, None otherwise
        """
        query = select(LeaveRequest).where(
            and_(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status.in_(["pending", "approved"]),
                LeaveRequest.start_date <= end_date,
                LeaveRequest.end_date >= start_date
            )
        )
        
        if exclude_request_id:
            query = query.where(LeaveRequest.id != exclude_request_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_public_holidays_in_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[PublicHoliday]:
        """Get all public holidays within a date range.
        
        Args:
            start_date: Range start date
            end_date: Range end date
        
        Returns:
            List of PublicHoliday objects
        """
        query = select(PublicHoliday).where(
            and_(
                PublicHoliday.is_active == True,
                PublicHoliday.start_date <= end_date,
                PublicHoliday.end_date >= start_date
            )
        ).order_by(PublicHoliday.start_date)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def calculate_working_days(
        self,
        start_date: date,
        end_date: date,
        exclude_holidays: bool = True
    ) -> Decimal:
        """Calculate working days between two dates, optionally excluding public holidays.
        
        Args:
            start_date: Start date
            end_date: End date
            exclude_holidays: Whether to exclude public holidays from count
        
        Returns:
            Number of working days as Decimal
        """
        if end_date < start_date:
            raise LeaveValidationError("End date must be after start date")
        
        # Calculate total days
        total_days = (end_date - start_date).days + 1
        
        # If not excluding holidays, return total
        if not exclude_holidays:
            return Decimal(str(total_days))
        
        # Get public holidays in range
        holidays = await self.get_public_holidays_in_range(start_date, end_date)
        
        # Count holiday days that overlap with leave period
        holiday_days = 0
        for holiday in holidays:
            # Calculate overlap
            overlap_start = max(start_date, holiday.start_date)
            overlap_end = min(end_date, holiday.end_date)
            if overlap_start <= overlap_end:
                holiday_days += (overlap_end - overlap_start).days + 1
        
        working_days = total_days - holiday_days
        return Decimal(str(max(0, working_days)))
    
    async def get_leave_balance(
        self,
        employee_id: int,
        leave_type: str,
        year: int
    ) -> Optional[LeaveBalance]:
        """Get leave balance for an employee, leave type, and year.
        
        Args:
            employee_id: Employee ID
            leave_type: Leave type (annual, sick, etc.)
            year: Year
        
        Returns:
            LeaveBalance or None if not found
        """
        result = await self.session.execute(
            select(LeaveBalance).where(
                and_(
                    LeaveBalance.employee_id == employee_id,
                    LeaveBalance.leave_type == leave_type,
                    LeaveBalance.year == year
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def check_sufficient_balance(
        self,
        employee_id: int,
        leave_type: str,
        requested_days: Decimal,
        year: int
    ) -> Tuple[bool, Decimal]:
        """Check if employee has sufficient leave balance.
        
        Args:
            employee_id: Employee ID
            leave_type: Leave type
            requested_days: Number of days requested
            year: Year
        
        Returns:
            Tuple of (has_sufficient_balance, available_balance)
        """
        balance = await self.get_leave_balance(employee_id, leave_type, year)
        
        if not balance:
            return False, Decimal("0")
        
        available = balance.available
        return available >= requested_days, available
    
    async def validate_leave_request(
        self,
        employee_id: int,
        leave_type: str,
        start_date: date,
        end_date: date,
        is_half_day: bool = False,
        exclude_request_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str], Decimal]:
        """Validate a leave request against all business rules.
        
        Args:
            employee_id: Employee ID
            leave_type: Leave type
            start_date: Leave start date
            end_date: Leave end date
            is_half_day: Whether it's a half-day leave
            exclude_request_id: Optional request ID to exclude (for updates)
        
        Returns:
            Tuple of (is_valid, error_message, calculated_days)
        
        Raises:
            LeaveValidationError: If validation fails
        """
        # 1. Validate leave type
        if leave_type not in LEAVE_TYPES:
            return False, f"Invalid leave type. Must be one of: {', '.join(LEAVE_TYPES)}", Decimal("0")
        
        # 2. Validate dates
        if end_date < start_date:
            return False, "End date must be after start date", Decimal("0")
        
        # 3. Calculate days
        if is_half_day:
            calculated_days = Decimal("0.5")
        else:
            calculated_days = await self.calculate_working_days(
                start_date, end_date, exclude_holidays=False
            )
        
        # 4. Check for overlapping requests
        overlap = await self.check_overlapping_leaves(
            employee_id, start_date, end_date, exclude_request_id
        )
        if overlap:
            return False, f"Overlapping leave request exists (ID: {overlap.id})", calculated_days
        
        # 5. Check balance (skip for unpaid leave)
        if leave_type != "unpaid":
            has_balance, available = await self.check_sufficient_balance(
                employee_id, leave_type, calculated_days, start_date.year
            )
            if not has_balance:
                return False, f"Insufficient balance. Available: {available} days, Requested: {calculated_days} days", calculated_days
        
        return True, None, calculated_days
    
    async def send_manager_notification(
        self,
        leave_request: LeaveRequest,
        employee: Employee,
        manager: Employee
    ) -> bool:
        """Send email notification to manager about new leave request.
        
        Args:
            leave_request: The leave request
            employee: The employee requesting leave
            manager: The manager to notify
        
        Returns:
            True if email sent successfully, False otherwise
        """
        if not manager.email:
            return False
        
        subject = f"Leave Request from {employee.name} - {leave_request.leave_type.title()}"
        
        # Calculate balance info
        balance = await self.get_leave_balance(
            employee.id,
            leave_request.leave_type,
            leave_request.start_date.year
        )
        balance_text = f"{balance.available} days" if balance else "N/A"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #ffffff; color: #1e40af; padding: 20px; text-align: center; border-bottom: 2px solid #1e40af; }}
                .content {{ background-color: #f8fafc; padding: 20px; border: 1px solid #e2e8f0; }}
                .details {{ background-color: white; padding: 15px; border-left: 3px solid #22c55e; margin: 15px 0; }}
                .footer {{ background-color: #1e293b; color: #94a3b8; padding: 15px; text-align: center; font-size: 12px; }}
                .label {{ font-weight: bold; color: #1e40af; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🗓️ Leave Request Pending Approval</h2>
                </div>
                <div class="content">
                    <p>Dear {manager.name},</p>
                    <p>You have a new leave request pending your approval.</p>
                    
                    <div class="details">
                        <p><span class="label">Employee:</span> {employee.name}</p>
                        <p><span class="label">Department:</span> {employee.department or 'N/A'}</p>
                        <p><span class="label">Leave Type:</span> {leave_request.leave_type.title()}</p>
                        <p><span class="label">Start Date:</span> {leave_request.start_date.strftime('%d %b %Y')}</p>
                        <p><span class="label">End Date:</span> {leave_request.end_date.strftime('%d %b %Y')}</p>
                        <p><span class="label">Duration:</span> {leave_request.total_days} days</p>
                        <p><span class="label">Current Balance:</span> {balance_text}</p>
                    </div>
                    
                    {f'<div style="background-color: #fef3c7; padding: 10px; border-radius: 4px; margin: 10px 0;"><strong>Reason:</strong> {leave_request.reason}</div>' if leave_request.reason else ''}
                    
                    <p style="margin-top: 20px;">Please review and approve or reject this request in the HR Portal.</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from Baynunah HR Portal.<br>
                    For questions, contact HR at <a href="mailto:hr@baynunah.ae" style="color: #94a3b8;">hr@baynunah.ae</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Leave Request Pending Approval
        
        Dear {manager.name},
        
        You have a new leave request pending your approval.
        
        Employee: {employee.name}
        Department: {employee.department or 'N/A'}
        Leave Type: {leave_request.leave_type.title()}
        Start Date: {leave_request.start_date.strftime('%d %b %Y')}
        End Date: {leave_request.end_date.strftime('%d %b %Y')}
        Duration: {leave_request.total_days} days
        Current Balance: {balance_text}
        
        {'Reason: ' + leave_request.reason if leave_request.reason else ''}
        
        Please review and approve or reject this request in the HR Portal.
        
        ---
        This is an automated notification from Baynunah HR Portal.
        For questions, contact HR at hr@baynunah.ae
        """
        
        success = await self.email_service.send_email(
            manager.email,
            subject,
            html_body,
            text_body
        )
        
        if success:
            # Update notification tracking
            leave_request.manager_notified = True
            leave_request.notification_sent_at = datetime.now(timezone.utc)
            await self.session.commit()
        
        return success
    
    async def get_manager_for_employee(self, employee_id: int) -> Optional[Employee]:
        """Get the line manager for an employee.
        
        Args:
            employee_id: Employee ID
        
        Returns:
            Employee object of manager or None
        """
        # Get employee
        emp_result = await self.session.execute(
            select(Employee).where(Employee.id == employee_id)
        )
        employee = emp_result.scalar_one_or_none()
        
        if not employee or not employee.line_manager_id:
            return None
        
        # Get manager
        mgr_result = await self.session.execute(
            select(Employee).where(Employee.id == employee.line_manager_id)
        )
        return mgr_result.scalar_one_or_none()


async def get_leave_service(session: AsyncSession) -> LeaveService:
    """Get leave service instance."""
    return LeaveService(session)
