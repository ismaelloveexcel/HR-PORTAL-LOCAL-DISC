from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.audit_log import AuditLog
from typing import List, Optional

class AuditLogRepository:
    async def create(self, session: AsyncSession, **kwargs) -> AuditLog:
        log = AuditLog(**kwargs)
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return log

    async def list(self, session: AsyncSession, entity: Optional[str] = None, user_id: Optional[str] = None) -> List[AuditLog]:
        query = select(AuditLog)
        if entity:
            query = query.where(AuditLog.entity == entity)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        result = await session.execute(query.order_by(AuditLog.timestamp.desc()))
        return result.scalars().all()
