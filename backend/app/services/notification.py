from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationCreate, NotificationResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def create(self, session: AsyncSession, data: NotificationCreate) -> NotificationResponse:
        notification = await self.repo.create(session, **data.dict())
        return NotificationResponse.from_orm(notification)

    async def list(self, session: AsyncSession, user_id: Optional[str] = None, unread_only: bool = False) -> List[NotificationResponse]:
        notifications = await self.repo.list(session, user_id, unread_only)
        return [NotificationResponse.from_orm(n) for n in notifications]

    async def mark_read(self, session: AsyncSession, notification_id: int) -> Optional[NotificationResponse]:
        notification = await self.repo.mark_read(session, notification_id)
        return NotificationResponse.from_orm(notification) if notification else None
