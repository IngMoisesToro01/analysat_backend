from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

password_config = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hashed(password: str) -> str:
  return password_config.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return password_config.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
  data_to_encode = data.copy()
  expire_time = (datetime.now(timezone.utc) + timedelta(minutes=30))
  data_to_encode.update({ "exp": expire_time })

  return jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
  try:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
  except jwt.ExpiredSignatureError:
    raise ValueError("Token expirado")
  except jwt.InvalidTokenError:
    raise ValueError("Token inválido")
