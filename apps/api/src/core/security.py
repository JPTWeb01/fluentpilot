import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import UUID

import bcrypt
import jwt

from src.core.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def hash_token(token: str) -> str:
    """Refresh tokens are stored hashed so a leaked DB doesn't hand out valid tokens."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _create_token(
    subject: UUID, expires_delta: timedelta, token_type: Literal["access", "refresh"]
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        # jti guarantees uniqueness even when two tokens for the same user are minted
        # within the same second (iat/exp are truncated to whole seconds by JWT encoding,
        # so without it identical-payload tokens would collide on the refresh_tokens hash index).
        "jti": uuid.uuid4().hex,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: UUID) -> str:
    return _create_token(user_id, timedelta(minutes=settings.access_token_expire_minutes), "access")


def create_refresh_token(user_id: UUID) -> str:
    return _create_token(user_id, timedelta(days=settings.refresh_token_expire_days), "refresh")


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
