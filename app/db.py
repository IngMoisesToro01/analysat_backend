from fastapi import Depends, FastAPI
from typing import Annotated
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
  raise ValueError("DATABASE_URL no está definido en el archivo .env")

engine = create_engine(DATABASE_URL)

def get_session():
  with Session(engine) as session:
    yield session

def initialize_database(app: FastAPI):
  from app.models import user as user_model  # noqa: F401
  from app.models import project as project_model  # noqa: F401
  from app.models import task as task_model  # noqa: F401

  SQLModel.metadata.create_all(engine)
  yield

SessionDependency = Annotated[Session, Depends(get_session)]
