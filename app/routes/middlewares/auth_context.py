from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from sqlmodel import Session

from app.db import engine
from app.models.user import User
from app.credentials.security import decode_access_token

PROTECTED_PREFIXES = ("/projects", "/tasks")

class AuthMiddleware(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
    request.state.user = None

    authorization: Optional[str] = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
      token = authorization.split(" ", 1)[1].strip()
      try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if user_id is not None:
          with Session(engine) as session:
            user = session.get(User, int(user_id))
            if user:
              request.state.user = user
      except Exception:
        request.state.user = None

    path: str = request.url.path or ""
    if path.startswith(PROTECTED_PREFIXES) and request.state.user is None:
      return JSONResponse(
        status_code=401,
        content={"detail": "Not authenticated"}
      )

    response = await call_next(request)
    return response
