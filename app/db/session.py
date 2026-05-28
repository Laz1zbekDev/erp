from typing import AsyncGenerator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..core.settings import settings

url = URL.create(
    drivername="postgresql+asyncpg",
    host=settings.db_host,
    port=settings.db_port,
    password=settings.db_pass,
    database=settings.db_name,
    username=settings.db_user,
)

engine = create_async_engine(
    url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            print("rollback qilindi")
            await session.rollback()
            raise
