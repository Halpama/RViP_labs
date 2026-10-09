import os
import subprocess
import sys
from pathlib import Path

DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
if DATABASE_URL:
    os.environ.setdefault("DATABASE_URL", DATABASE_URL)

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import get_session
from app.main import app

READER_ROOT = Path(__file__).parents[2] / "reader-service"


@pytest_asyncio.fixture
async def session():
    if not DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL or DATABASE_URL is required")
    engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1))
    environment = {**os.environ, "DATABASE_URL": DATABASE_URL}
    try:
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=READER_ROOT,
                       env=environment, check=True)
    except subprocess.CalledProcessError as error:
        await engine.dispose()
        pytest.skip(f"PostgreSQL is unavailable: {error}")
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as db_session:
        yield db_session
    subprocess.run([sys.executable, "-m", "alembic", "downgrade", "base"], cwd=READER_ROOT,
                   env=environment, check=True)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(session):
    async def override_session():
        yield session
    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
