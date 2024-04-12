from sqlalchemy.future import select
from ..models.models import Image


async def get_image(db, image_id: int):
    result = await db.execute(select(Image).filter(Image.id == image_id))
    return result.scalars().first()

async def get_image_by_title(db, title: str):
    result = await db.execute(select(Image).filter(Image.title == title))
    return result.scalars().first()

async def create_image(db, image: Image):
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image

async def update_image(db, image_id: int, image_data: dict):
    await db.execute(Image.__table__.update().where(Image.id == image_id).values(image_data))
    await db.commit()
    return await get_image(db, image_id)

async def delete_image(db, image_id: int):
    image = await get_image(db, image_id)
    db.delete(image)
    await db.commit()
    return image