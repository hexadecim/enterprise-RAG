"""
database.py – Async SQLAlchemy engine + session factory.

Uses asyncpg as the async driver (postgresql+asyncpg://...).
Call `create_all_tables()` on startup to bootstrap the schema in dev/test;
in production prefer Alembic migrations.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,          # detect stale connections
    pool_size=10,
    max_overflow=20,
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,      # keep attributes accessible after commit
    autoflush=False,
    autocommit=False,
)


# ---------------------------------------------------------------------------
# Declarative base (shared by all models)
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# FastAPI dependency – yields a session per request
# ---------------------------------------------------------------------------
async def get_db() -> AsyncSession:  # type: ignore[return]
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Dev/test helper – creates tables from the ORM metadata
# ---------------------------------------------------------------------------
async def create_all_tables() -> None:
    """Create all tables defined in Base.metadata (dev/test only)."""
    # Import models so their metadata is registered before create_all
    import backend.models  # noqa: F401  # side-effect import

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
