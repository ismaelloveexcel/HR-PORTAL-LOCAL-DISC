"""Background task scheduler for attendance-related tasks.

This module provides:
- 10:00 AM daily manager email
- 9:30 AM missing clock-in reminder
- 5:30 PM missing clock-out reminder

Uses APScheduler for task scheduling.
Install with: pip install apscheduler
"""
import logging
from typing import Optional

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    AsyncIOScheduler = None
    CronTrigger = None

from sqlalchemy import select

from app.database import async_session_maker
from app.models.employee import Employee
from app.services.attendance_service import AttendanceService

logger = logging.getLogger(__name__)


class AttendanceScheduler:
    """Scheduler for attendance background tasks."""
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.is_running = False
    
    def start(self):
        """Start the scheduler."""
        if not APSCHEDULER_AVAILABLE:
            logger.warning("APScheduler not installed. Background tasks disabled.")
            logger.warning("Install with: pip install apscheduler")
            return
        
        if self.is_running:
            logger.warning("Scheduler already running")
            return
        
        self.scheduler = AsyncIOScheduler()
        
        # 9:30 AM UAE (5:30 UTC) - Clock-in reminder
        self.scheduler.add_job(
            self._send_clockin_reminders,
            CronTrigger(hour=5, minute=30, timezone="UTC"),  # 9:30 AM UAE
            id="clockin_reminder",
            name="Clock-in Reminder"
        )
        
        # 10:00 AM UAE (6:00 UTC) - Manager daily summary
        self.scheduler.add_job(
            self._send_manager_summaries,
            CronTrigger(hour=6, minute=0, timezone="UTC"),  # 10:00 AM UAE
            id="manager_summary",
            name="Manager Daily Summary"
        )
        
        # 5:30 PM UAE (13:30 UTC) - Clock-out reminder
        self.scheduler.add_job(
            self._send_clockout_reminders,
            CronTrigger(hour=13, minute=30, timezone="UTC"),  # 5:30 PM UAE
            id="clockout_reminder",
            name="Clock-out Reminder"
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("Attendance scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler and self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Attendance scheduler stopped")
    
    async def _send_clockin_reminders(self):
        """Send clock-in reminders to employees who haven't clocked in."""
        logger.info("Running clock-in reminder task")
        try:
            async with async_session_maker() as session:
                service = AttendanceService(session)
                count = await service.send_missing_clockin_reminders()
                logger.info(f"Sent {count} clock-in reminders")
        except Exception as e:
            logger.error(f"Error sending clock-in reminders: {e}")
    
    async def _send_clockout_reminders(self):
        """Send clock-out reminders to employees who haven't clocked out."""
        logger.info("Running clock-out reminder task")
        try:
            async with async_session_maker() as session:
                service = AttendanceService(session)
                count = await service.send_missing_clockout_reminders()
                logger.info(f"Sent {count} clock-out reminders")
        except Exception as e:
            logger.error(f"Error sending clock-out reminders: {e}")
    
    async def _send_manager_summaries(self):
        """Send daily attendance summary to all managers."""
        logger.info("Running manager summary email task")
        try:
            async with async_session_maker() as session:
                # Get all managers
                result = await session.execute(
                    select(Employee).where(
                        Employee.role.in_(["manager", "admin", "hr"])
                    )
                )
                managers = result.scalars().all()
                
                service = AttendanceService(session)
                success_count = 0
                
                for manager in managers:
                    # Check if manager has team members
                    team_result = await session.execute(
                        select(Employee.id).where(
                            Employee.line_manager_id == manager.id
                        ).limit(1)
                    )
                    has_team = team_result.scalar_one_or_none()
                    
                    if has_team:
                        success = await service.send_manager_daily_summary_email(manager.id)
                        if success:
                            success_count += 1
                
                logger.info(f"Sent {success_count} manager summary emails")
        except Exception as e:
            logger.error(f"Error sending manager summaries: {e}")
    
    async def trigger_now(self, task_name: str) -> dict:
        """Manually trigger a task immediately.
        
        Args:
            task_name: One of "clockin_reminder", "clockout_reminder", "manager_summary"
        
        Returns:
            Result dictionary with status
        """
        tasks = {
            "clockin_reminder": self._send_clockin_reminders,
            "clockout_reminder": self._send_clockout_reminders,
            "manager_summary": self._send_manager_summaries
        }
        
        if task_name not in tasks:
            return {"status": "error", "message": f"Unknown task: {task_name}"}
        
        try:
            await tasks[task_name]()
            return {"status": "success", "message": f"Task {task_name} completed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Singleton instance
_scheduler: Optional[AttendanceScheduler] = None


def get_attendance_scheduler() -> AttendanceScheduler:
    """Get or create the attendance scheduler singleton."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AttendanceScheduler()
    return _scheduler


def start_attendance_scheduler():
    """Start the attendance scheduler (call from app startup)."""
    scheduler = get_attendance_scheduler()
    scheduler.start()


def stop_attendance_scheduler():
    """Stop the attendance scheduler (call from app shutdown)."""
    scheduler = get_attendance_scheduler()
    scheduler.stop()
