import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import schemas
from .database import models

async def get_section(owner: str, section_id: int, session: AsyncSession) -> models.Section | None:
    query = select(models.Section).where(models.Section.owner == owner, models.Section.id == section_id)
    query_result = (await session.execute(query)).scalars().one_or_none()
    return query_result

async def update_section(section_id: int, new_section: schemas.SectionUpdate, owner:str, session: AsyncSession) -> models.Section | None:
    section = await get_section(owner=owner, section_id=section_id, session=session)
    if section:
        section.name = new_section.name
        await session.commit()
        return section
    else:
        return None

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

async def delete_section(section_id: int, owner: str, session: AsyncSession) -> bool:
    section = await get_section(owner=owner, section_id=section_id, session=session)
    if not section:
        return False
    await session.delete(section)
    await session.commit()
    return True

async def get_tasks(section_id: int, owner:str, session: AsyncSession, skip = 0, limit = 100) -> list[models.Task]:
    query = select(models.Task).offset(skip).limit(limit).where(models.Task.section_id == section_id, models.Task.owner == owner)
    return (await session.execute(query)).scalars().all()


async def get_task(section_id: int, task_id: int, owner:str, session: AsyncSession) -> models.Task:
    query = select(models.Task).where(
        models.Task.section_id == section_id, 
        models.Task.owner == owner,
        models.Task.id == task_id
    )
    return (await session.execute(query)).scalars().one_or_none()


async def create_task(section_id: int, task_create: schemas.TaskCreate, owner: str, session: AsyncSession) -> models.Task:
    section = await get_section(owner=owner, section_id=section_id, session=session)
    if not section:
        return None

    task = models.Task(
        name = task_create.name,
        description = task_create.description,
        completed = False,
        created_at = datetime.datetime.now(),
        owner = owner,
        section_id = section.id
    )
    
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    return task

async def delete_task(section_id: int, task_id:int, owner: str, session: AsyncSession) -> bool:
    section = await get_section(owner=owner, section_id=section_id, session=session)
    if not section:
        return False
    
    task = await get_task(section_id, task_id, owner, session)
    if not task:
        return False

    await session.delete(task)
    await session.commit()
    return True


async def update_task(section_id: int, task_id: int, task_update: schemas.TaskUpdate, owner: str, session: AsyncSession) -> models.Task:
    section = await get_section(owner=owner, section_id=section_id, session=session)
    if not section:
        return None
    
    task = await get_task(section_id, task_id, owner, session)
    if not task:
        return None
    
    for var, value in vars(task_update).items():
        setattr(task, var, value) if value else None

    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    return task
