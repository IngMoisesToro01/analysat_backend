from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import select, Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_session
from app.models.user import User
from app.models.schemas import Token, UserRead, UserData, LoginRequest
from app.credentials.security import (
  get_password_hashed,
  verify_password,
  create_access_token
)
from app.credentials.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
  user_data: UserData,
  session: Session = Depends(get_session)
):
  query = select(User).where(User.email == user_data.email)
  result = session.exec(query)
  exists_user = result.first()

  if exists_user:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail="El email ya está registrado"
    )

  hashed_password = get_password_hashed(user_data.password)
  
  new_user = User(
    name=user_data.name,
    email=user_data.email,
    password_hash=hashed_password
  )

  session.add(new_user)
  session.commit()
  session.refresh(new_user)

  return new_user

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_user(
  request: Request,
  session: Session = Depends(get_session)
):
  content_type = request.headers.get("content-type", "")
  
  if "application/json" in content_type:
    body = await request.json()
    email = body.get("email")
    password = body.get("password")
  else:
    form_data = await request.form()
    email = form_data.get("username")
    password = form_data.get("password")
  
  if not email or not password:
    raise HTTPException(status_code=400, detail="Se requiere email/username y password")

  query = select(User).where(User.email == email)
  result = session.exec(query)
  user = result.first()

  if not user or not verify_password(password, user.password_hash):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Credenciales inválidas"
    )

  access_token = create_access_token(data={ "user_id": str(user.id) })

  return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def get_current_user_info(
  current_user: User = Depends(get_current_user)
):
  return current_user
