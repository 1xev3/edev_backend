from pydantic import BaseModel, Field
import typing, datetime

class TaskCreate(BaseModel):
    name: typing.Optional[str] = Field(title="Task name", default="Task")
    description: typing.Optional[str] = Field(title="Task description", default="")

class TaskUpdate(TaskCreate):
    completed: typing.Optional[bool] = Field(title="Task is completed?", default=False)
    completed_at: typing.Optional[datetime.datetime] = Field(title="Task must be completed at?", default=None)

class Task(TaskUpdate):
    id: int = Field(title="Task ID")
    created_at: datetime.datetime = Field(title="Task created at")
    
    