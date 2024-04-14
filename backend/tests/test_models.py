import pytest
from backend.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv
import os

dot_path = find_dotenv()
load_dotenv(dot_path)
DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture(scope="session")
async def async_session() -> AsyncSession:
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session


@pytest.mark.asyncio
async def test_create_user(async_session: AsyncSession):
    async with async_session() as session:  # Await the async session directly
        async with session.begin():
            user = User(username="testuser", email="test@example.com")
            session.add(user)
            await session.commit()
            assert user.id is not None
