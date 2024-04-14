import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.models.models import Base, User, Image

from dotenv import load_dotenv, find_dotenv
import os


dot_path = find_dotenv()
load_dotenv(dot_path)
DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture
async def db_session():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        db_session = async_session()
        yield db_session
    finally:
        await db_session.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_db_connection(db_session):
    # If the fixture setup succeeds, the database connection is considered successful
    assert db_session is not None
