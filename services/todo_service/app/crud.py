import logging, typing

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import schemas
from .database import models

async def get_sections(session: AsyncSession, owner:str, skip: int = 0, limit: int = 100) -> list[models.Section]:
    query = select(models.Section).offset(skip).limit(limit).where(models.Section.owner == owner)
    query_result = (await session.execute(query)).scalars().all()
    return query_result

async def create_section(section:schemas.SectionCreate, owner:str, session: AsyncSession) -> models.Section:
    new_section = models.Section(
        name=section.name,
        owner=owner,
    )
    session.add(new_section)
    await session.commit()
    return new_section