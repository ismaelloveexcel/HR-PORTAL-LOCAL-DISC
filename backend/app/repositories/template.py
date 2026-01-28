from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.template import Template
from typing import List, Optional

class TemplateRepository:
    async def create(self, session: AsyncSession, **kwargs) -> Template:
        template = Template(**kwargs)
        session.add(template)
        await session.commit()
        await session.refresh(template)
        return template

    async def get(self, session: AsyncSession, template_id: int) -> Optional[Template]:
        result = await session.execute(select(Template).where(Template.id == template_id))
        return result.scalar_one_or_none()

    async def list(self, session: AsyncSession, type: Optional[str] = None) -> List[Template]:
        query = select(Template)
        if type:
            query = query.where(Template.type == type)
        result = await session.execute(query.order_by(Template.name))
        return result.scalars().all()

    async def update(self, session: AsyncSession, template: Template, **kwargs) -> Template:
        for k, v in kwargs.items():
            setattr(template, k, v)
        await session.commit()
        await session.refresh(template)
        return template

    async def create_revision(self, session: AsyncSession, parent: Template, **kwargs) -> Template:
        version = parent.version + 1
        revision = Template(
            **kwargs,
            parent_id=parent.id,
            version=version,
            name=parent.name,
            type=parent.type,
            created_by=kwargs.get('created_by', parent.created_by),
            is_active=True
        )
        session.add(revision)
        await session.commit()
        await session.refresh(revision)
        return revision

    async def deactivate(self, session: AsyncSession, template: Template) -> Template:
        template.is_active = False
        await session.commit()
        await session.refresh(template)
        return template
