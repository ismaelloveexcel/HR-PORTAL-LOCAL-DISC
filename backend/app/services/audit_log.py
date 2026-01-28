from app.repositories.audit_log import AuditLogRepository
from app.schemas.audit_log import AuditLogBase, AuditLogResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

class AuditLogService:
    def __init__(self, repo: AuditLogRepository):
        self.repo = repo

    async def log_action(self, session: AsyncSession, data: AuditLogBase) -> AuditLogResponse:
        log = await self.repo.create(session, **data.dict())
        return AuditLogResponse.from_orm(log)

    async def list(self, session: AsyncSession, entity: Optional[str] = None, user_id: Optional[str] = None) -> List[AuditLogResponse]:
        logs = await self.repo.list(session, entity, user_id)
        return [AuditLogResponse.from_orm(l) for l in logs]
