"""
تنظیمات دیتابیس با SQLAlchemy Async
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import event

from config import settings


class Base(DeclarativeBase):
    """کلاس پایه مدل‌ها"""
    pass


# ایجاد engine ناهمزمان
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# ایجاد session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """وابستگی برای دریافت session دیتابیس"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """ایجاد تمام جداول دیتابیس"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
