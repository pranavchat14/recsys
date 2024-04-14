import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.models.models import User

client = TestClient(app)


@pytest.mark.asyncio
async def test_create_user(db_session):
    async with db_session() as session:
        async with session.begin():
            new_user = User(
                username="test_user",
                email="test@example.com",
                hashed_password="hashed_pwd",
            )
            session.add(new_user)
        await session.commit()

    async with db_session() as session:
        result = await session.execute("SELECT * FROM users WHERE username='test_user'")
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.username == "test_user"
