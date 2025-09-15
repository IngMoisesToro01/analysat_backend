from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, projects, tasks
from app.db import initialize_database
from app.routes.middlewares.auth_context import AuthMiddleware

app = FastAPI(
  title='Gestión de Proyectos y Tareas',
  version='1.0.0',
  description='API para manejar usuarios, proyectos y tareas con FastAPI + PostgreSQL hecho por Moises Toro',
  lifespan=initialize_database
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)

@app.get('/')
async def root():
  return { 'message': '🚀 Bienvenido a la API de gestión de proyectos y tareas' }
