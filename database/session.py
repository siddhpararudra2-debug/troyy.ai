"""
Database session management for Engineering OS.
"""
import logging
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine
)
from sqlalchemy.pool import NullPool

from database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(
        self,
        database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/engineering_os",
        echo: bool = False,
    ):
        self.database_url = database_url
        self._engine = None
        self._session_factory = None
        self.echo = echo

    async def initialize(self):
        """Initialize the database connection pool."""
        self._engine = create_async_engine(
            self.database_url,
            echo=self.echo,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info(f"Database connected: {self.database_url}")

    async def create_tables(self):
        """Create all database tables."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")

    async def drop_tables(self):
        """Drop all database tables (use with caution)."""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.warning("Database tables dropped")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self):
        """Close the database connection."""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connection closed")

    @property
    def session_factory(self):
        return self._session_factory


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    async for session in db_manager.get_session():
        yield session