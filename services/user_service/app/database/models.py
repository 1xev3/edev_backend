from fastapi import Depends

from sqlalchemy import (
    Column, 
    ForeignKey, 
    Integer, 
    String,
    LargeBinary,
    Boolean
)
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, relationship

from app.database import db

class Group(db.BASE):
    __tablename__  = 'group'
    __table_args__ = {'schema':  db.SCHEMA}

    id = Column(Integer, primary_key=True , autoincrement=True, index=True)
    name = Column(String)


class User(db.BASE):
    __tablename__ = "users"
    __table_args__ = {'schema':  db.SCHEMA}

    id = Column(Integer, nullable=False, primary_key=True)

    email = Column(String(225), nullable=False, unique=True)
    hashed_password = Column(String(), nullable=False)
    nickname = Column(String(225), nullable=False)
    is_active = Column(Boolean, default=False)

    group_id = mapped_column(ForeignKey(f"{db.SCHEMA}.group.id"))
    group = relationship("Group", uselist=False)

async def get_user_db(session: AsyncSession, email:str):
    return (await session.execute(select(User).filter(User.email == email))).scalars().first()

# async def get_user_db(session: AsyncSession = Depends(db.get_async_session)):
#     yield SQLAlchemyUserDatabase(session, User)