from app.repositories.template import TemplateRepository
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse
from app.models.template import Template
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

class TemplateService:
    def __init__(self, repo: TemplateRepository):
        self.repo = repo

    async def create(self, session: AsyncSession, data: TemplateCreate, created_by: str) -> TemplateResponse:
        template = await self.repo.create(session, **data.dict(), created_by=created_by, version=1, is_active=True)
        return TemplateResponse.from_orm(template)

    async def get(self, session: AsyncSession, template_id: int) -> Optional[TemplateResponse]:
        template = await self.repo.get(session, template_id)
        return TemplateResponse.from_orm(template) if template else None

    async def list(self, session: AsyncSession, type: Optional[str] = None) -> List[TemplateResponse]:
        templates = await self.repo.list(session, type)
        return [TemplateResponse.from_orm(t) for t in templates]

    async def update(self, session: AsyncSession, template_id: int, data: TemplateUpdate) -> Optional[TemplateResponse]:
        template = await self.repo.get(session, template_id)
        if not template:
            return None
        updated = await self.repo.update(session, template, **data.dict(exclude_unset=True))
        return TemplateResponse.from_orm(updated)

    async def create_revision(self, session: AsyncSession, template_id: int, data: TemplateCreate, created_by: str) -> Optional[TemplateResponse]:
        parent = await self.repo.get(session, template_id)
        if not parent:
            return None
        revision = await self.repo.create_revision(session, parent, **data.dict(), created_by=created_by)
        return TemplateResponse.from_orm(revision)

    async def deactivate(self, session: AsyncSession, template_id: int) -> Optional[TemplateResponse]:
        template = await self.repo.get(session, template_id)
        if not template:
            return None
        deactivated = await self.repo.deactivate(session, template)
        return TemplateResponse.from_orm(deactivated)
