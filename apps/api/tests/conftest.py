from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.core.rate_limit import limiter
from src.db.base import Base
from src.deps import get_db
from src.main import app


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield session_factory

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    # The limiter's in-memory storage is a module-level singleton shared across
    # the whole pytest process; without resetting it here, tests that hit
    # rate-limited endpoints (e.g. /auth/register) would accumulate counts
    # across unrelated test files and start failing with 429s.
    limiter.reset()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
