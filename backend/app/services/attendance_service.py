"""Attendance service for enhanced features.

This service provides:
1. Background job scheduling for 10:00 AM manager email
2. Leave integration with attendance
3. Timesheet generation and approval
4. Attendance analytics
5. Push notification setup
6. Geofence validation
7. Public holiday integration
"""
import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.models.attendance import AttendanceRecord, WORK_LOCATIONS
from app.models.leave import LeaveRequest, LeaveBalance
from app.models.public_holiday import PublicHoliday
from app.models.timesheet import Timesheet
from app.models.geofence import Geofence, is_within_geofence
from app.models.notification import Notification
from app.services.email_service import get_email_service
from app.core.time import get_uae_today

logger = logging.getLogger(__name__)


class AttendanceService:
    """Enhanced attendance service with all integrations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.email_service = get_email_service()
    
    # ==================== LEAVE INTEGRATION ====================
    
    async def is_employee_on_leave(self, employee_id: int, check_date: date) -> Optional[LeaveRequest]:
        """Check if employee has approved leave for a specific date."""
        result = await self.session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.employee_id == employee_id,
                    LeaveRequest.status == "approved",
                    LeaveRequest.start_date <= check_date,
                    LeaveRequest.end_date >= check_date
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_leave_balance(self, employee_id: int, year: int) -> List[LeaveBalance]:
        """Get all leave balances for an employee for a year."""
        result = await self.session.execute(
            select(LeaveBalance).where(
                and_(
                    LeaveBalance.employee_id == employee_id,
                    LeaveBalance.year == year
                )
            )
        )
        return result.scalars().all()
    
    async def create_leave_request(
        self,
        employee_id: int,
        leave_type: str,
        start_date: date,
        end_date: date,
        is_half_day: bool = False,
        half_day_type: Optional[str] = None,
        reason: Optional[str] = None
    ) -> LeaveRequest:
        """Create a new leave request."""
        # Calculate total days
        if is_half_day:
            total_days = Decimal("0.5")
        else:
            # Count weekdays between dates (excluding Fridays for 6-day, Fri+Sat for 5-day)
            # Simplified: just count calendar days for now
            delta = (end_date - start_date).days + 1
            total_days = Decimal(str(delta))
        
        leave_request = LeaveRequest(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            is_half_day=is_half_day,
            half_day_type=half_day_type,
            total_days=total_days,
            reason=reason,
            status="pending"
        )
        
        self.session.add(leave_request)
        await self.session.commit()
        await self.session.refresh(leave_request)
        
        return leave_request
    
    # ==================== PUBLIC HOLIDAY INTEGRATION ====================
    
    async def is_public_holiday(self, check_date: date) -> Optional[PublicHoliday]:
        """Check if a date is a public holiday."""
        result = await self.session.execute(
            select(PublicHoliday).where(
                and_(
                    PublicHoliday.is_active == True,
                    PublicHoliday.start_date <= check_date,
                    PublicHoliday.end_date >= check_date
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_holidays_for_year(self, year: int) -> List[PublicHoliday]:
        """Get all public holidays for a year."""
        result = await self.session.execute(
            select(PublicHoliday).where(
                and_(
                    PublicHoliday.year == year,
                    PublicHoliday.is_active == True
                )
            ).order_by(PublicHoliday.start_date)
        )
        return result.scalars().all()
    
    # ==================== GEOFENCE VALIDATION ====================
    
    async def validate_geofence(
        self,
        user_lat: float,
        user_lon: float,
        work_location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate GPS coordinates against geofences."""
        # Get all active geofences
        result = await self.session.execute(
            select(Geofence).where(Geofence.is_active == True)
        )
        geofences = result.scalars().all()
        
        if not geofences:
            return {
                "is_valid": True,
                "message": "No geofences configured",
                "validation_required": False
            }
        
        # If work_location specified, check that specific geofence
        if work_location:
            for gf in geofences:
                if gf.name == work_location:
                    is_within, distance = is_within_geofence(
                        user_lat, user_lon,
                        float(gf.latitude), float(gf.longitude),
                        gf.radius_meters
                    )
                    return {
                        "is_valid": is_within or not gf.validation_required,
                        "work_location": work_location,
                        "matched_geofence": gf.name if is_within else None,
                        "distance_meters": distance,
                        "within_radius": is_within,
                        "validation_required": gf.validation_required,
                        "message": f"Within {gf.name}" if is_within else f"{distance:.0f}m from {gf.name}"
                    }
        
        # Otherwise, find nearest geofence
        nearest = None
        nearest_distance = float('inf')
        matched = None
        
        for gf in geofences:
            is_within, distance = is_within_geofence(
                user_lat, user_lon,
                float(gf.latitude), float(gf.longitude),
                gf.radius_meters
            )
            if is_within:
                matched = gf
                nearest_distance = distance
                break
            if distance < nearest_distance:
                nearest = gf
                nearest_distance = distance
        
        if matched:
            return {
                "is_valid": True,
                "work_location": matched.name,
                "matched_geofence": matched.name,
                "distance_meters": nearest_distance,
                "within_radius": True,
                "validation_required": matched.validation_required,
                "message": f"Location detected: {matched.name}"
            }
        
        return {
            "is_valid": False,
            "work_location": None,
            "matched_geofence": None,
            "distance_meters": nearest_distance,
            "within_radius": False,
            "validation_required": nearest.validation_required if nearest else False,
            "message": f"Outside all geofences. Nearest: {nearest.name} ({nearest_distance:.0f}m)" if nearest else "No geofences found"
        }
    
    # ==================== TIMESHEET GENERATION ====================
    
    async def generate_monthly_timesheet(
        self,
        employee_id: int,
        year: int,
        month: int
    ) -> Timesheet:
        """Generate monthly timesheet from attendance records."""
        # Check if timesheet already exists
        existing = await self.session.execute(
            select(Timesheet).where(
                and_(
                    Timesheet.employee_id == employee_id,
                    Timesheet.year == year,
                    Timesheet.month == month
                )
            )
        )
        timesheet = existing.scalar_one_or_none()
        
        if timesheet and timesheet.status not in ["draft", "rejected"]:
            return timesheet  # Don't regenerate if already submitted
        
        # Get all attendance records for the month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        records_result = await self.session.execute(
            select(AttendanceRecord).where(
                and_(
                    AttendanceRecord.employee_id == employee_id,
                    AttendanceRecord.attendance_date >= start_date,
                    AttendanceRecord.attendance_date <= end_date
                )
            )
        )
        records = records_result.scalars().all()
        
        # Calculate totals
        total_present = 0
        total_absent = 0
        total_wfh = 0
        total_late = 0
        total_early = 0
        total_regular_hours = Decimal("0")
        total_overtime = Decimal("0")
        total_night_ot = Decimal("0")
        total_holiday_ot = Decimal("0")
        total_ot_amount = Decimal("0")
        offset_earned = Decimal("0")
        food_days = 0
        food_total = Decimal("0")
        
        # Location counts
        loc_head_office = 0
        loc_kezad = 0
        loc_safario = 0
        loc_sites = 0
        loc_meeting = 0
        loc_event = 0
        
        has_issues = False
        issues = []
        
        for record in records:
            if record.status == "present" or record.status == "late":
                total_present += 1
            elif record.status == "absent":
                total_absent += 1
            
            if record.work_location == "Work From Home":
                total_wfh += 1
            elif record.work_location == "Head Office":
                loc_head_office += 1
            elif record.work_location == "KEZAD":
                loc_kezad += 1
            elif record.work_location == "Safario":
                loc_safario += 1
            elif record.work_location == "Sites":
                loc_sites += 1
            elif record.work_location == "Meeting":
                loc_meeting += 1
            elif record.work_location == "Event":
                loc_event += 1
            
            if record.is_late:
                total_late += 1
            if record.is_early_departure:
                total_early += 1
            
            if record.regular_hours:
                total_regular_hours += record.regular_hours
            if record.overtime_hours:
                total_overtime += record.overtime_hours
            if record.is_night_overtime and record.overtime_hours:
                total_night_ot += record.overtime_hours
            if record.is_holiday_overtime and record.overtime_hours:
                total_holiday_ot += record.overtime_hours
            if record.overtime_amount:
                total_ot_amount += record.overtime_amount
            if record.offset_hours_earned:
                offset_earned += record.offset_hours_earned
            
            if record.food_allowance_eligible:
                food_days += 1
                if record.food_allowance_amount:
                    food_total += record.food_allowance_amount
            
            if record.exceeds_daily_limit or record.exceeds_overtime_limit:
                has_issues = True
                issues.append(f"{record.attendance_date}: Exceeded limits")
        
        # Calculate working days (simplified)
        total_working_days = (end_date - start_date).days + 1
        weekends = sum(1 for d in range(total_working_days) 
                      if (start_date + timedelta(days=d)).weekday() in [4, 5])  # Fri, Sat
        total_working_days -= weekends
        
        # Get leave days
        leaves_result = await self.session.execute(
            select(LeaveRequest).where(
                and_(
                    LeaveRequest.employee_id == employee_id,
                    LeaveRequest.status == "approved",
                    LeaveRequest.start_date <= end_date,
                    LeaveRequest.end_date >= start_date
                )
            )
        )
        leaves = leaves_result.scalars().all()
        total_leave = sum(l.total_days for l in leaves)
        
        # Create or update timesheet
        if not timesheet:
            timesheet = Timesheet(
                employee_id=employee_id,
                year=year,
                month=month,
                status="draft"
            )
            self.session.add(timesheet)
        
        # Update fields
        timesheet.total_working_days = total_working_days
        timesheet.total_present_days = total_present
        timesheet.total_absent_days = total_absent
        timesheet.total_leave_days = total_leave
        timesheet.total_wfh_days = total_wfh
        timesheet.total_late_arrivals = total_late
        timesheet.total_early_departures = total_early
        timesheet.total_regular_hours = total_regular_hours
        timesheet.total_overtime_hours = total_overtime
        timesheet.total_night_overtime_hours = total_night_ot
        timesheet.total_holiday_overtime_hours = total_holiday_ot
        timesheet.total_overtime_amount = total_ot_amount
        timesheet.offset_hours_earned = offset_earned
        timesheet.days_at_head_office = loc_head_office
        timesheet.days_at_kezad = loc_kezad
        timesheet.days_at_safario = loc_safario
        timesheet.days_at_sites = loc_sites
        timesheet.days_at_meeting = loc_meeting
        timesheet.days_at_event = loc_event
        timesheet.food_allowance_days = food_days
        timesheet.food_allowance_total = food_total
        timesheet.has_compliance_issues = has_issues
        timesheet.compliance_notes = "; ".join(issues) if issues else None
        
        await self.session.commit()
        await self.session.refresh(timesheet)
        
        return timesheet
    
    # ==================== ANALYTICS ====================
    
    async def get_monthly_analytics(self, year: int, month: int) -> Dict[str, Any]:
        """Get monthly attendance analytics."""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Get all records for the month
        result = await self.session.execute(
            select(AttendanceRecord).where(
                and_(
                    AttendanceRecord.attendance_date >= start_date,
                    AttendanceRecord.attendance_date <= end_date
                )
            )
        )
        records = result.scalars().all()
        
        # Get total employees
        emp_result = await self.session.execute(
            select(func.count(Employee.id)).where(Employee.is_active == True)
        )
        total_employees = emp_result.scalar() or 0
        
        if not records:
            return {
                "year": year,
                "month": month,
                "total_employees": total_employees,
                "total_records": 0,
                "message": "No attendance data for this period"
            }
        
        # Calculate metrics
        total_records = len(records)
        present_count = sum(1 for r in records if r.status in ["present", "late"])
        late_count = sum(1 for r in records if r.is_late)
        total_overtime = sum(r.overtime_hours or Decimal("0") for r in records)
        night_overtime = sum(r.overtime_hours or Decimal("0") for r in records if r.is_night_overtime)
        holiday_overtime = sum(r.overtime_hours or Decimal("0") for r in records if r.is_holiday_overtime)
        total_ot_cost = sum(r.overtime_amount or Decimal("0") for r in records)
        
        # Location breakdown
        loc_counts = {loc: 0 for loc in WORK_LOCATIONS}
        for r in records:
            if r.work_location in loc_counts:
                loc_counts[r.work_location] += 1
        
        # Compliance
        issues_count = sum(1 for r in records if r.exceeds_daily_limit or r.exceeds_overtime_limit)
        
        return {
            "year": year,
            "month": month,
            "total_employees": total_employees,
            "total_records": total_records,
            "present_rate": round(present_count / total_records * 100, 1) if total_records else 0,
            "late_rate": round(late_count / total_records * 100, 1) if total_records else 0,
            "avg_overtime_hours": round(float(total_overtime) / total_employees, 2) if total_employees else 0,
            "total_overtime_hours": float(total_overtime),
            "night_overtime_hours": float(night_overtime),
            "holiday_overtime_hours": float(holiday_overtime),
            "regular_overtime_hours": float(total_overtime - night_overtime - holiday_overtime),
            "total_overtime_cost": float(total_ot_cost),
            "location_breakdown": {
                loc: {"count": count, "percentage": round(count / total_records * 100, 1) if total_records else 0}
                for loc, count in loc_counts.items()
            },
            "compliance_issues": issues_count,
            "compliance_rate": round((total_records - issues_count) / total_records * 100, 1) if total_records else 100
        }
    
    # ==================== NOTIFICATIONS ====================
    
    async def create_attendance_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "attendance",
        link: Optional[str] = None
    ) -> Notification:
        """Create an attendance-related notification."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type,
            link=link
        )
        self.session.add(notification)
        await self.session.commit()
        return notification
    
    async def send_missing_clockin_reminders(self) -> int:
        """Send reminders to employees who haven't clocked in today.
        
        Should be called at ~9:30 AM.
        Returns count of reminders sent.
        """
        today = get_uae_today()
        
        # Get all active employees
        emp_result = await self.session.execute(
            select(Employee).where(Employee.is_active == True)
        )
        employees = emp_result.scalars().all()
        
        # Get today's attendance records
        att_result = await self.session.execute(
            select(AttendanceRecord.employee_id).where(
                AttendanceRecord.attendance_date == today
            )
        )
        clocked_in_ids = {r for r in att_result.scalars().all()}
        
        count = 0
        for emp in employees:
            if emp.id not in clocked_in_ids:
                # Check if on leave
                leave = await self.is_employee_on_leave(emp.id, today)
                if leave:
                    continue
                
                # Check if holiday
                holiday = await self.is_public_holiday(today)
                if holiday:
                    continue
                
                # Send notification
                await self.create_attendance_notification(
                    user_id=str(emp.id),
                    title="Clock-in Reminder",
                    message="You haven't clocked in yet today. Please clock in to record your attendance.",
                    notification_type="reminder",
                    link="/attendance"
                )
                count += 1
        
        await self.session.commit()
        return count
    
    async def send_missing_clockout_reminders(self) -> int:
        """Send reminders to employees who clocked in but haven't clocked out.
        
        Should be called at ~5:30 PM.
        Returns count of reminders sent.
        """
        today = get_uae_today()
        
        # Get records with clock_in but no clock_out
        result = await self.session.execute(
            select(AttendanceRecord).where(
                and_(
                    AttendanceRecord.attendance_date == today,
                    AttendanceRecord.clock_in.isnot(None),
                    AttendanceRecord.clock_out.is_(None)
                )
            )
        )
        records = result.scalars().all()
        
        count = 0
        for record in records:
            await self.create_attendance_notification(
                user_id=str(record.employee_id),
                title="Clock-out Reminder",
                message="Don't forget to clock out before leaving. Your attendance record is incomplete.",
                notification_type="reminder",
                link="/attendance"
            )
            count += 1
        
        await self.session.commit()
        return count
    
    # ==================== MANAGER EMAIL ====================
    
    async def send_manager_daily_summary_email(self, manager_id: int) -> bool:
        """Send daily attendance summary email to manager.
        
        Should be called at 10:00 AM.
        """
        # Get manager
        manager_result = await self.session.execute(
            select(Employee).where(Employee.id == manager_id)
        )
        manager = manager_result.scalar_one_or_none()
        if not manager or not manager.email:
            return False
        
        # Get team members
        team_result = await self.session.execute(
            select(Employee).where(
                and_(
                    Employee.line_manager_id == manager_id,
                    Employee.is_active == True
                )
            )
        )
        team = team_result.scalars().all()
        
        if not team:
            return False
        
        today = get_uae_today()
        
        # Build summary table
        rows = []
        for emp in team:
            # Get attendance
            att_result = await self.session.execute(
                select(AttendanceRecord).where(
                    and_(
                        AttendanceRecord.employee_id == emp.id,
                        AttendanceRecord.attendance_date == today
                    )
                )
            )
            record = att_result.scalar_one_or_none()
            
            # Check leave
            leave = await self.is_employee_on_leave(emp.id, today)
            
            if leave:
                status = "On Leave"
                location = "—"
                last_update = "—"
                remarks = leave.leave_type.replace("_", " ").title()
            elif not record or not record.clock_in:
                status = "Not Checked In"
                location = "—"
                last_update = "—"
                remarks = "—"
            else:
                status = "Present"
                location = record.work_location or "—"
                last_update = record.clock_in.strftime("%H:%M") if record.clock_in else "—"
                remarks = record.location_remarks or "—"
                if location == "Work From Home":
                    remarks = "Approved" if record.wfh_approval_confirmed else "Not Approved"
            
            rows.append({
                "name": emp.name,
                "status": status,
                "location": location,
                "last_update": last_update,
                "remarks": remarks
            })
        
        # Generate HTML table
        table_html = """
        <table style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;">
            <thead>
                <tr style="background-color: #1e293b; color: white;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #e2e8f0;">Employee</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #e2e8f0;">Status</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #e2e8f0;">Work Location</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #e2e8f0;">Last Update</th>
                    <th style="padding: 12px; text-align: left; border: 1px solid #e2e8f0;">Remarks</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for row in rows:
            status_color = {
                "Present": "#22c55e",
                "On Leave": "#3b82f6",
                "Not Checked In": "#ef4444"
            }.get(row["status"], "#6b7280")
            
            table_html += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;">{row['name']}</td>
                    <td style="padding: 10px; border: 1px solid #e2e8f0; color: {status_color}; font-weight: bold;">{row['status']}</td>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;">{row['location']}</td>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;">{row['last_update']}</td>
                    <td style="padding: 10px; border: 1px solid #e2e8f0;">{row['remarks']}</td>
                </tr>
            """
        
        table_html += "</tbody></table>"
        
        # Counts
        present_count = sum(1 for r in rows if r["status"] == "Present")
        leave_count = sum(1 for r in rows if r["status"] == "On Leave")
        not_in_count = sum(1 for r in rows if r["status"] == "Not Checked In")
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #1e293b; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f8fafc; padding: 20px; border: 1px solid #e2e8f0; }}
                .footer {{ background-color: #1e293b; color: #94a3b8; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; }}
                .summary {{ display: flex; gap: 20px; margin-bottom: 20px; }}
                .stat {{ background: white; padding: 15px; border-radius: 8px; text-align: center; flex: 1; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                .stat-value {{ font-size: 24px; font-weight: bold; }}
                .stat-label {{ color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 Daily Attendance Summary</h1>
                    <p>{today.strftime('%A, %B %d, %Y')}</p>
                </div>
                <div class="content">
                    <p>Good morning {manager.name},</p>
                    <p>Here's your team's attendance status as of 10:00 AM:</p>
                    
                    <div class="summary">
                        <div class="stat">
                            <div class="stat-value" style="color: #22c55e;">{present_count}</div>
                            <div class="stat-label">Present</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" style="color: #3b82f6;">{leave_count}</div>
                            <div class="stat-label">On Leave</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value" style="color: #ef4444;">{not_in_count}</div>
                            <div class="stat-label">Not Checked In</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{len(rows)}</div>
                            <div class="stat-label">Total Team</div>
                        </div>
                    </div>
                    
                    {table_html}
                    
                    <p style="margin-top: 20px; color: #6b7280; font-size: 12px;">
                        This is an automated daily summary. For detailed attendance data, please log in to the HR Portal.
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated message from Baynunah HR Portal.<br>
                    For questions, contact <a href="mailto:hr@baynunah.ae" style="color: #94a3b8;">hr@baynunah.ae</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"📋 Team Attendance Summary - {today.strftime('%B %d, %Y')}"
        
        return await self.email_service.send_email(
            to_email=manager.email,
            subject=subject,
            html_body=html_body
        )
