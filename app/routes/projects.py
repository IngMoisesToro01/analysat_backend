from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from app.db import get_session
from app.models.project import Project, ProjectCreate, ProjectUpdate
from app.models.user import User
from app.credentials.dependencies import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
  project: ProjectCreate,
  session: Session = Depends(get_session),
  current_user: User = Depends(get_current_user)
):
  new_project = Project(**project.dict(), user_id=current_user.id)
  session.add(new_project)
  session.commit()
  session.refresh(new_project)
  return new_project

@router.get("/", response_model=list[Project])
async def list_projects(
  session: Session = Depends(get_session),
  name: str | None = None,
  current_user: User = Depends(get_current_user)
):
  query = select(Project).where(Project.user_id == current_user.id)
  if name:
    query = query.where(Project.name.contains(name))
  result = session.exec(query)
  return result.all()

@router.get("/{project_id}", response_model=Project)
async def get_project(
  project_id: int,
  session: Session = Depends(get_session),
  current_user: User = Depends(get_current_user)
):
  project = session.get(Project, project_id)
  if not project or project.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Proyecto no encontrado")
  return project

@router.put("/{project_id}", response_model=Project)
async def update_project(
  project_id: int,
  project_update: ProjectUpdate,
  session: Session = Depends(get_session),
  current_user: User = Depends(get_current_user)
):
  project = session.get(Project, project_id)
  if not project or project.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Proyecto no encontrado")

  for key, value in project_update.dict(exclude_unset=True).items():
    setattr(project, key, value)

  session.add(project)
  session.commit()
  session.refresh(project)
  return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
  project_id: int,
  session: Session = Depends(get_session),
  current_user: User = Depends(get_current_user)
):
  project = session.get(Project, project_id)
  if not project or project.user_id != current_user.id:
    raise HTTPException(status_code=404, detail="Proyecto no encontrado")

  session.delete(project)
  session.commit()
  return None
