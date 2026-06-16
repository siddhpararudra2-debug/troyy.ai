"""
Troy — Solver Tests Configuration
Pytest fixtures and configuration for solver service tests.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory, engine
from app.main import _register_all_formulas, SCHEMA_SQL

# Trigger registration of all domain formulas
_register_all_formulas()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """Ensure all database tables exist before running any tests."""
    async with engine.begin() as conn:
        for statement in SCHEMA_SQL.strip().split(";"):
            stmt = statement.strip()
            if stmt:
                await conn.execute(text(stmt))
    yield


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide a transactional database session rolled back after every test."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()
