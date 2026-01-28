from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogCreate


class ActivityLogService:
    async def create_log(
        self,
        session: AsyncSession,
        data: ActivityLogCreate
    ) -> ActivityLog:
        log_entry = ActivityLog(
            candidate_id=data.candidate_id,
            stage=data.stage,
            action_type=data.action_type,
            action_description=data.action_description,
            performed_by=data.performed_by,
            performed_by_id=data.performed_by_id,
            timestamp=datetime.utcnow(),
            visibility=data.visibility
        )
        session.add(log_entry)
        await session.commit()
        await session.refresh(log_entry)
        return log_entry

    async def get_candidate_logs(
        self,
        session: AsyncSession,
        candidate_id: int,
        include_internal: bool = False
    ) -> List[ActivityLog]:
        query = select(ActivityLog).where(
            ActivityLog.candidate_id == candidate_id
        )
        
        if not include_internal:
            query = query.where(ActivityLog.visibility == "candidate")
        
        query = query.order_by(desc(ActivityLog.timestamp))
        
        result = await session.execute(query)
        return list(result.scalars().all())

    async def log_action(
        self,
        session: AsyncSession,
        candidate_id: int,
        stage: str,
        action_type: str,
        description: str,
        performed_by: str,
        performed_by_id: Optional[str] = None,
        visibility: str = "internal"
    ) -> ActivityLog:
        data = ActivityLogCreate(
            candidate_id=candidate_id,
            stage=stage,
            action_type=action_type,
            action_description=description,
            performed_by=performed_by,
            performed_by_id=performed_by_id,
            visibility=visibility
        )
        return await self.create_log(session, data)


activity_log_service = ActivityLogService()
