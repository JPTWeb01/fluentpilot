from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from src.modules.auth.models import User
from src.modules.auth.repository import RefreshTokenRepository, UserRepository
from src.modules.auth.schemas import TokenResponse

settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._refresh_tokens = RefreshTokenRepository(db)

    async def register(
        self, *, email: str, password: str, full_name: str | None
    ) -> tuple[User, TokenResponse]:
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "An account with this email already exists."
            )

        user = await self._users.create(
            email=email, hashed_password=hash_password(password), full_name=full_name
        )
        tokens = await self._issue_tokens(user)
        await self._db.commit()
        return user, tokens

    async def login(self, *, email: str, password: str) -> tuple[User, TokenResponse]:
        user = await self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password.")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "This account has been deactivated.")

        tokens = await self._issue_tokens(user)
        await self._db.commit()
        return user, tokens

    async def refresh(self, *, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except Exception as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token.") from exc

        if payload.get("type") != "refresh":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token.")

        token_hash = hash_token(refresh_token)
        stored = await self._refresh_tokens.get_valid_by_hash(token_hash)
        if stored is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token expired or revoked.")

        user = await self._users.get_by_id(stored.user_id)
        if user is None or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token.")

        # Rotate on use: revoke the presented token and issue a fresh pair, so a
        # replayed/stolen refresh token can only ever be used once.
        await self._refresh_tokens.revoke(token_hash)
        tokens = await self._issue_tokens(user)
        await self._db.commit()
        return tokens

    async def logout(self, *, refresh_token: str) -> None:
        await self._refresh_tokens.revoke(hash_token(refresh_token))
        await self._db.commit()

    async def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        await self._refresh_tokens.create(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
