from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

# Convert sync PostgreSQL URL to async
def get_async_database_url(database_url: str) -> str:
    """Convert PostgreSQL URL to async version for asyncpg."""
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url

# Create async engine
engine = create_async_engine(
    get_async_database_url(settings.database_url),
    echo=settings.environment == "development",
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create base class for models
Base = declarative_base()

# Metadata for Alembic
metadata = MetaData()


async def get_async_session() -> AsyncSession:
    """
    Dependency to get async database session.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    """
    await engine.dispose() 