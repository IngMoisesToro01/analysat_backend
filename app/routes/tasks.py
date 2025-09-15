from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from app.db import get_session
from app.models.task import Task, TaskCreate, TaskUpdate
from app.models.user import User
from app.models.project import Project
from app.credentials.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
	task: TaskCreate,
	session: Session = Depends(get_session),
	current_user: User = Depends(get_current_user)
):
	project = session.get(Project, task.project_id)
	
	if not project or project.user_id != current_user.id:
		raise HTTPException(status_code=403, detail="No puedes añadir tareas a este proyecto")

	new_task = Task(**task.dict(), user_id=current_user.id)
	session.add(new_task)
	session.commit()
	session.refresh(new_task)
	return new_task

@router.get("/", response_model=list[Task])
async def list_tasks(
	session: Session = Depends(get_session),
	status: str | None = None,
	project_id: int | None = None,
	current_user: User = Depends(get_current_user)
):
	query = select(Task).where(Task.user_id == current_user.id)

	if status:
		query = query.where(Task.status == status)
	if project_id:
		query = query.where(Task.project_id == project_id)

	result = session.exec(query)
	return result.all()

@router.get("/{task_id}", response_model=Task)
async def get_task(
	task_id: int,
	session: Session = Depends(get_session),
	current_user: User = Depends(get_current_user)
):
	task = session.get(Task, task_id)

	if not task or task.user_id != current_user.id:
		raise HTTPException(status_code=404, detail="Tarea no encontrada")

	return task

@router.put("/{task_id}", response_model=Task)
async def update_task(
	task_id: int,
	task_update: TaskUpdate,
	session: Session = Depends(get_session),
	current_user: User = Depends(get_current_user)
):
	task = session.get(Task, task_id)

	if not task or task.user_id != current_user.id:
		raise HTTPException(status_code=404, detail="Tarea no encontrada")

	for key, value in task_update.dict(exclude_unset=True).items():
		setattr(task, key, value)

	session.add(task)
	session.commit()
	session.refresh(task)
	return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
	task_id: int,
	session: Session = Depends(get_session),
	current_user: User = Depends(get_current_user)
):
	task = session.get(Task, task_id)

	if not task or task.user_id != current_user.id:
		raise HTTPException(status_code=404, detail="Tarea no encontrada")

	session.delete(task)
	session.commit()
	return None
