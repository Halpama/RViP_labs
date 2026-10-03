import os
import subprocess
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
SERVICE_ROOT = Path(__file__).parents[1]


@pytest_asyncio.fixture
async def session():
    if not DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL or DATABASE_URL is required for PostgreSQL tests")
    engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1))
    environment = {**os.environ, "DATABASE_URL": DATABASE_URL}
    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=SERVICE_ROOT,
            env=environment,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        await engine.dispose()
        pytest.skip(f"PostgreSQL is unavailable for migration-backed tests: {error}")
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as db_session:
        yield db_session
    subprocess.run(
        [sys.executable, "-m", "alembic", "downgrade", "base"],
        cwd=SERVICE_ROOT,
        env=environment,
        check=True,
    )
    await engine.dispose()
