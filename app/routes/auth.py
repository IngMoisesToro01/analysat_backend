from fastapi import APIRouter, Depends, HTTPException, status
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
  login_data: LoginRequest | None = None,
  form_data: OAuth2PasswordRequestForm = Depends(),
  session: Session = Depends(get_session)
):
  email = login_data.email if login_data is not None else form_data.username
  password = login_data.password if login_data is not None else form_data.password

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
