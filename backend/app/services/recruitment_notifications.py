"""
Recruitment notification service for automated communications.
Supports solo HR by automating interview reminders, offer expiry alerts, etc.
"""
import logging
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recruitment import (
    RecruitmentRequest, Candidate, Interview, Offer
)
from app.services.email_service import EmailService
from app.services.notification import NotificationService

logger = logging.getLogger(__name__)


class RecruitmentNotificationService:
    """Service for automated recruitment notifications."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.notification_service = NotificationService()
    
    async def send_interview_reminder(
        self,
        session: AsyncSession,
        interview: Interview,
        candidate: Candidate,
        hours_before: int = 24
    ) -> bool:
        """
        Send interview reminder to candidate.
        
        Args:
            session: Database session
            interview: Interview object
            candidate: Candidate object
            hours_before: Hours before interview to send reminder
            
        Returns:
            True if notification sent successfully
        """
        if not interview.scheduled_date or not candidate.email:
            return False
        
        # Check if reminder should be sent
        now = datetime.now(timezone.utc)
        reminder_time = interview.scheduled_date - timedelta(hours=hours_before)
        
        if now < reminder_time:
            return False  # Too early
        
        # Get recruitment request for position details
        result = await session.execute(
            select(RecruitmentRequest).where(
                RecruitmentRequest.id == interview.recruitment_request_id
            )
        )
        request = result.scalar_one_or_none()
        
        if not request:
            return False
        
        # Format interview details
        interview_date = interview.scheduled_date.strftime("%A, %B %d, %Y")
        interview_time = interview.scheduled_date.strftime("%I:%M %p")
        
        # Build email content
        subject = f"Interview Reminder: {request.position_title}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Interview Reminder</h2>
            <p>Dear {candidate.full_name},</p>
            
            <p>This is a friendly reminder about your upcoming interview:</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Position:</strong> {request.position_title}</p>
                <p><strong>Department:</strong> {request.department}</p>
                <p><strong>Date:</strong> {interview_date}</p>
                <p><strong>Time:</strong> {interview_time}</p>
                <p><strong>Duration:</strong> {interview.duration_minutes} minutes</p>
                {f'<p><strong>Location:</strong> {interview.location}</p>' if interview.location else ''}
                {f'<p><strong>Meeting Link:</strong> <a href="{interview.meeting_link}">{interview.meeting_link}</a></p>' if interview.meeting_link else ''}
            </div>
            
            <p><strong>Interview Type:</strong> {interview.interview_type.replace('_', ' ').title()}</p>
            
            <p>Please ensure you:</p>
            <ul>
                <li>Join on time (or arrive 10 minutes early for in-person interviews)</li>
                <li>Have a stable internet connection (for video interviews)</li>
                <li>Bring any requested documents</li>
                <li>Prepare questions for the interviewer</li>
            </ul>
            
            <p>If you need to reschedule, please contact HR as soon as possible.</p>
            
            <p>We look forward to meeting you!</p>
            
            <p>Best regards,<br>HR Team</p>
        </body>
        </html>
        """
        
        text_body = f"""
        Interview Reminder
        
        Dear {candidate.full_name},
        
        This is a friendly reminder about your upcoming interview:
        
        Position: {request.position_title}
        Department: {request.department}
        Date: {interview_date}
        Time: {interview_time}
        Duration: {interview.duration_minutes} minutes
        {'Location: ' + interview.location if interview.location else ''}
        {'Meeting Link: ' + interview.meeting_link if interview.meeting_link else ''}
        
        Interview Type: {interview.interview_type.replace('_', ' ').title()}
        
        Please ensure you join on time and are prepared.
        
        Best regards,
        HR Team
        """
        
        # Send email
        success = await self.email_service.send_email(
            to_email=candidate.email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        
        if success:
            logger.info(f"Interview reminder sent to {candidate.email} for interview {interview.interview_number}")
        
        return success
    
    async def send_offer_expiry_alert(
        self,
        session: AsyncSession,
        offer: Offer,
        candidate: Candidate,
        days_before: int = 3
    ) -> bool:
        """
        Send offer expiry alert to candidate and HR.
        
        Args:
            session: Database session
            offer: Offer object
            candidate: Candidate object
            days_before: Days before expiry to send alert
            
        Returns:
            True if notification sent successfully
        """
        if not offer.expires_at or not candidate.email:
            return False
        
        # Check if alert should be sent
        now = datetime.now(timezone.utc)
        alert_time = offer.expires_at - timedelta(days=days_before)
        
        if now < alert_time:
            return False  # Too early
        
        if offer.status in ['accepted', 'declined', 'withdrawn', 'expired']:
            return False  # Offer already finalized
        
        # Calculate days remaining
        days_remaining = (offer.expires_at - now).days
        
        # Build email content
        subject = f"Action Required: Job Offer Expires in {days_remaining} Day{'s' if days_remaining != 1 else ''}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Offer Expiry Reminder</h2>
            <p>Dear {candidate.full_name},</p>
            
            <p><strong style="color: #ff6b6b;">Your job offer will expire in {days_remaining} day{'s' if days_remaining != 1 else ''}.</strong></p>
            
            <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                <p><strong>Position:</strong> {offer.position_title}</p>
                <p><strong>Department:</strong> {offer.department}</p>
                <p><strong>Offer Number:</strong> {offer.offer_number}</p>
                <p><strong>Expires:</strong> {offer.expires_at.strftime("%B %d, %Y at %I:%M %p")}</p>
            </div>
            
            <p>Please review and respond to the offer before it expires. If you have any questions or need more time, contact HR immediately.</p>
            
            <p><strong>To accept or decline the offer, please log into your candidate portal or contact HR.</strong></p>
            
            <p>Best regards,<br>HR Team</p>
        </body>
        </html>
        """
        
        text_body = f"""
        Offer Expiry Reminder
        
        Dear {candidate.full_name},
        
        Your job offer will expire in {days_remaining} day{'s' if days_remaining != 1 else ''}.
        
        Position: {offer.position_title}
        Department: {offer.department}
        Offer Number: {offer.offer_number}
        Expires: {offer.expires_at.strftime("%B %d, %Y at %I:%M %p")}
        
        Please review and respond to the offer before it expires.
        
        Best regards,
        HR Team
        """
        
        # Send email to candidate
        success = await self.email_service.send_email(
            to_email=candidate.email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )
        
        if success:
            logger.info(f"Offer expiry alert sent to {candidate.email} for offer {offer.offer_number}")
        
        return success
    
    async def check_and_send_interview_reminders(
        self,
        session: AsyncSession,
        hours_before: int = 24
    ) -> int:
        """
        Check all scheduled interviews and send reminders for those happening soon.
        
        Args:
            session: Database session
            hours_before: Hours before interview to send reminder
            
        Returns:
            Number of reminders sent
        """
        now = datetime.now(timezone.utc)
        reminder_window_start = now
        reminder_window_end = now + timedelta(hours=hours_before + 1)  # +1 hour buffer
        
        # Find interviews scheduled in the reminder window
        result = await session.execute(
            select(Interview).where(
                and_(
                    Interview.status == 'scheduled',
                    Interview.scheduled_date.isnot(None),
                    Interview.scheduled_date >= reminder_window_start,
                    Interview.scheduled_date <= reminder_window_end
                )
            )
        )
        interviews = result.scalars().all()
        
        sent_count = 0
        for interview in interviews:
            # Get candidate
            candidate_result = await session.execute(
                select(Candidate).where(Candidate.id == interview.candidate_id)
            )
            candidate = candidate_result.scalar_one_or_none()
            
            if candidate:
                success = await self.send_interview_reminder(
                    session, interview, candidate, hours_before
                )
                if success:
                    sent_count += 1
        
        logger.info(f"Sent {sent_count} interview reminders")
        return sent_count
    
    async def check_and_send_offer_expiry_alerts(
        self,
        session: AsyncSession,
        days_before: int = 3
    ) -> int:
        """
        Check all pending offers and send expiry alerts for those expiring soon.
        
        Args:
            session: Database session
            days_before: Days before expiry to send alert
            
        Returns:
            Number of alerts sent
        """
        now = datetime.now(timezone.utc)
        alert_window_start = now
        alert_window_end = now + timedelta(days=days_before + 1)  # +1 day buffer
        
        # Find offers expiring in the alert window
        result = await session.execute(
            select(Offer).where(
                and_(
                    Offer.status.in_(['sent', 'pending_approval', 'approved']),
                    Offer.expires_at.isnot(None),
                    Offer.expires_at >= alert_window_start,
                    Offer.expires_at <= alert_window_end
                )
            )
        )
        offers = result.scalars().all()
        
        sent_count = 0
        for offer in offers:
            # Get candidate
            candidate_result = await session.execute(
                select(Candidate).where(Candidate.id == offer.candidate_id)
            )
            candidate = candidate_result.scalar_one_or_none()
            
            if candidate:
                success = await self.send_offer_expiry_alert(
                    session, offer, candidate, days_before
                )
                if success:
                    sent_count += 1
        
        logger.info(f"Sent {sent_count} offer expiry alerts")
        return sent_count
    
    async def mark_expired_offers(self, session: AsyncSession) -> int:
        """
        Mark offers as expired if their expiry date has passed.
        
        Args:
            session: Database session
            
        Returns:
            Number of offers marked as expired
        """
        now = datetime.now(timezone.utc)
        
        # Find expired offers
        result = await session.execute(
            select(Offer).where(
                and_(
                    Offer.status.in_(['sent', 'pending_approval', 'approved']),
                    Offer.expires_at.isnot(None),
                    Offer.expires_at < now
                )
            )
        )
        offers = result.scalars().all()
        
        count = 0
        for offer in offers:
            offer.status = 'expired'
            count += 1
        
        if count > 0:
            await session.commit()
            logger.info(f"Marked {count} offers as expired")
        
        return count


# Singleton instance
recruitment_notification_service = RecruitmentNotificationService()
