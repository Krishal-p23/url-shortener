"""Async SQLAlchemy engine and request-scoped session dependency."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings


settings = get_settings()
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield one database session and close it after the request finishes."""

    async with SessionLocal() as session:
        yield session