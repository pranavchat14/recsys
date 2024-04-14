import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.models.models import Image


client = TestClient(app)


@pytest.mark.asyncio
async def test_create_image(db_session):
    async with db_session() as session:
        async with session.begin():
            new_image = Image(
                title="Test Image",
                file_path="path/to/image",
                primary_shape="circle",
                primary_color="red",
            )
            session.add(new_image)
        await session.commit()

    async with db_session() as session:
        result = await session.execute("SELECT * FROM images WHERE title='Test Image'")
        image = result.scalar_one_or_none()
        assert image is not None
        assert image.title == "Test Image"
        assert image.primary_shape == "circle"
        assert image.primary_color == "red"
