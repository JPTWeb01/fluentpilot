import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import decode_token
from src.db.session import get_db
from src.modules.auth.models import User
from src.modules.auth.repository import UserRepository

__all__ = ["get_db", "get_current_user"]

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
    except Exception as exc:
        raise credentials_exception from exc

    if payload.get("type") != "access":
        raise credentials_exception

    try:
        user_id = uuid.UUID(payload.get("sub"))
    except (TypeError, ValueError) as exc:
        raise credentials_exception from exc

    user = await UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user
