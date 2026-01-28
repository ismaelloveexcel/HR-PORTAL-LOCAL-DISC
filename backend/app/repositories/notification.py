from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.notification import Notification
from typing import List, Optional

class NotificationRepository:
    async def create(self, session: AsyncSession, **kwargs) -> Notification:
        notification = Notification(**kwargs)
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification

    async def list(self, session: AsyncSession, user_id: Optional[str] = None, unread_only: bool = False) -> List[Notification]:
        query = select(Notification)
        if user_id:
            query = query.where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.is_read == False)
        result = await session.execute(query.order_by(Notification.created_at.desc()))
        return result.scalars().all()

    async def mark_read(self, session: AsyncSession, notification_id: int) -> Optional[Notification]:
        notification = await session.get(Notification, notification_id)
        if notification:
            notification.is_read = True
            await session.commit()
            await session.refresh(notification)
        return notification
