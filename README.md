# Analysat Backend (FastAPI + SQLModel)

API de gestión de usuarios, proyectos y tareas construida con FastAPI, SQLModel y PostgreSQL.

## Requisitos

- Python 3.11
- PostgreSQL 13+
- pip / venv (o Poetry si prefieres)

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con:

```
DATABASE_URL=postgresql+psycopg2://<USER>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>
SECRET_KEY=<clave_secreta_larga_y_aleatoria>
ALGORITHM=HS256
```

Notas:
- `DATABASE_URL` usa el driver `psycopg2` (ya incluido vía `psycopg2`), ejemplo local: `postgresql+psycopg2://postgres:postgres@localhost:5432/analysat`.
- `SECRET_KEY` y `ALGORITHM` se usan para firmar los JWT.

## Instalación y ejecución

1. Crear y activar entorno virtual

```bash
python -m venv analysat
analysat/Scripts/activate  # Windows PowerShell
# source analysat/bin/activate  # Linux/Mac
```

2. Instalar dependencias

```bash
pip install -r requirements.txt
```

3. Configurar variables en `.env` (ver sección anterior).

4. Ejecutar servidor en desarrollo

```bash
fastapi dev
# o
uvicorn app.main:app --reload
```

- Documentación interactiva: `http://127.0.0.1:8000/docs`
- Health/root: `GET /`

## Autenticación y autorización

- Registro: `POST /auth/register`
- Login: `POST /auth/login`
  - JSON: `{ "email": "user@example.com", "password": "..." }`
  - También funciona con el diálogo "Authorize" de Swagger (OAuth2 Password): `username = email`, `password = contraseña`.
- Usa el token devuelto como `Authorization: Bearer <token>` para acceder a `/projects` y `/tasks`.

## Migraciones con Alembic

Este proyecto crea las tablas automáticamente en arranque (`SQLModel.metadata.create_all`). Para tener control de migraciones en equipo/producción, configura Alembic así:

1. Instalar Alembic

```bash
pip install alembic
```

2. Inicializar Alembic

```bash
alembic init migrations
```

3. Editar `alembic.ini`

- Cambia `sqlalchemy.url` para leer de `.env` o pon la misma URL de `DATABASE_URL`.
  - Sugerencia: deja `sqlalchemy.url =` vacío y carga la URL en `env.py`.

4. Editar `migrations/env.py`

Reemplaza el contenido relevante para usar el metadata de SQLModel:

```python
from sqlmodel import SQLModel
from app.db import engine

target_metadata = SQLModel.metadata

def run_migrations_offline():
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
```

5. Generar una nueva migración

```bash
alembic revision --autogenerate -m "init schema"
```

6. Aplicar migraciones

```bash
alembic upgrade head
```

7. Crear nuevas migraciones cuando cambien los modelos

```bash
alembic revision --autogenerate -m "add field X to Y"
alembic upgrade head
```

## Ejecución con Docker

Requisitos: Docker Desktop o Docker Engine + docker compose.

Archivos incluidos:
- `Dockerfile` (imagen de la app)
- `docker-compose.yml` (servicios app + Postgres)
- `.dockerignore`

Comandos básicos (desde la raíz del proyecto):

```bash
docker compose build
docker compose up -d
docker compose logs -f app
```

La app quedará en `http://localhost:8000` y la documentación en `http://localhost:8000/docs`.

Variables de entorno en contenedor:
- Por defecto, `docker-compose.yml` usa:
  - `DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/analysat`
  - `SECRET_KEY` configurable en tiempo de ejecución

Ejemplo de override al levantar:

```bash
SECRET_KEY=$(openssl rand -hex 32) docker compose up -d --build
```

Logs y administración:

```bash
docker compose logs -f app
docker compose logs -f db
docker compose ps
docker compose down
```

## Estructura relevante

```
app/
  main.py
  db.py
  models/
    user.py
    project.py
    task.py
    schemas.py
  routes/
    auth.py
    projects.py
    tasks.py
    middlewares/
      auth_context.py
```

## Notas de desarrollo

- El middleware `AuthMiddleware` protege `'/projects'` y `'/tasks'` cuando no hay token.
- Las entidades usan SQLModel; `ProjectCreate` y `TaskCreate` no aceptan `user_id` ni `created_at`; el servidor los asigna.

## Scripts útiles

```bash
uvicorn app.main:app --reload
pip list --outdated
```
