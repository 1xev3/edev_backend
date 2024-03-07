from fastapi import Depends

from sqlalchemy import (
    Column, 
    ForeignKey, 
    Integer, 
    String,
    DateTime,
    Boolean
)
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, relationship

from app.database import db

class Section(db.BASE):
    __tablename__ = 'sections'
    __table_args__ = {'schema':  db.SCHEMA}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    tasks = relationship('Task', back_populates='section', cascade="all, delete-orphan")

# Определяем модель сущности Task
class Task(db.BASE):
    __tablename__ = 'tasks'
    __table_args__ = {'schema':  db.SCHEMA}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    owner = Column(String, nullable=False)

    section_id = Column(Integer, ForeignKey(f'{db.SCHEMA}.sections.id'))
    section = relationship('Section', back_populates='tasks', foreign_keys=[])

# class Group(db.BASE):
#     __tablename__  = 'group'
#     __table_args__ = {'schema':  db.SCHEMA}

#     id = Column(Integer, primary_key=True , autoincrement=True, index=True)
#     name = Column(String)


# class User(db.BASE):
#     __tablename__ = "users"
#     __table_args__ = {'schema':  db.SCHEMA}

#     id = Column(Integer, nullable=False, primary_key=True)

#     email = Column(String(225), nullable=False, unique=True)
#     hashed_password = Column(String(), nullable=False)
#     nickname = Column(String(225), nullable=False)
#     is_active = Column(Boolean, default=False)

#     group_id = mapped_column(ForeignKey(f"{db.SCHEMA}.group.id"))
#     group = relationship("Group", uselist=False)