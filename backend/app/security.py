"""JWT 鉴权（FastAPI HTTPBearer 依赖）。auth_enabled=False 时放行匿名，便于本地联调。"""
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

settings = get_settings()
_security = HTTPBearer(auto_error=False)


def create_access_token(subject: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(
    creds: HTTPAuthorizationCredentials = Depends(_security),
) -> str:
    if not settings.auth_enabled:
        return "anonymous"
    if creds is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        payload = jwt.decode(
            creds.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload.get("sub", "anonymous")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
