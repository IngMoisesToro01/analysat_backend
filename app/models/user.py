from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime, timezone
from pydantic import EmailStr, BaseModel

if TYPE_CHECKING:
  from app.models.project import Project
  from app.models.task import Task

class UserBase(SQLModel):
  name: str = Field(default='', index=True)
  email: EmailStr = Field(default='', index=True, unique=True)
  password_hash: str = Field(default='', unique=True)
  created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class User(UserBase, table=True):
  __tablename__ = 'users'

  id: Optional[int] = Field(default=None, primary_key=True)
  projects: Optional[list["Project"]] = Relationship(back_populates="project_owner")
  tasks: Optional[list["Task"]] = Relationship(back_populates="task_owner")
  pass

class UserCreate(BaseModel):
  pass

class Token(BaseModel):
  access_token: str
  token_type: str = 'bearer'
