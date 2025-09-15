from __future__ import annotations
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

from app.models.user import User
from app.models.project import Project

if TYPE_CHECKING:
    pass

class TaskStatus(str, Enum):
    pending = 'pending'
    in_progress = 'in progress'
    completed = 'completed'

class TaskBase(SQLModel):
    title: str = Field(default='', index=True)
    description: str = Field(default='', index=True)
    status: TaskStatus = Field(default=TaskStatus.pending)

class Task(TaskBase, table=True):
    __tablename__ = 'tasks'

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    task_owner: "User" = Relationship(back_populates="tasks")
    project: "Project" = Relationship(back_populates="tasks")

class TaskCreate(SQLModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.pending
    project_id: int

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
