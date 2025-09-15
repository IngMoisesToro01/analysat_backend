from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime, timezone

from app.models.user import User

if TYPE_CHECKING:
    from app.models.task import Task

class ProjectBase(SQLModel):
    name: str = Field(default='', index=True)
    description: str = Field(default='', index=True)

class Project(ProjectBase, table=True):
    __tablename__ = 'projects'

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    project_owner: "User" = Relationship(back_populates="projects")
    tasks: list["Task"] = Relationship(back_populates="project")

class ProjectCreate(SQLModel):
    name: str
    description: str

class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
