from sqlalchemy.ext.asyncio import AsyncSession
import os
import json
import asyncio
from models.models import Image  # Adjust the import path as necessary
from database.database import SessionLocal, engine
from sqlalchemy.future import select

# Define the path to the JSON file containing image data
images_data_file = os.path.join(
    os.path.dirname(__file__), "..", "static", "images", "images_data.json"
)


async def ensure_image_table_exists():
    async with engine.begin() as conn:
        # Verify the existence of the Image table
        result = await conn.execute(select(1).select_from(Image.__table__).limit(1))
        table_exists = result.scalar()
        if not table_exists:
            # If the Image table does not exist, create it
            await conn.run_sync(Image.metadata.create_all)


async def insert_images(db_session: AsyncSession, images_data):
    async with db_session() as session:
        async with session.begin():
            for image_data in images_data:
                new_image = Image(
                    title=image_data["title"],
                    url=image_data["url"],
                    primary_shape=image_data["primary_shape"],
                    secondary_shape=image_data["secondary_shape"],
                    primary_color=image_data["primary_color"],
                    secondary_color=image_data["secondary_color"],
                    additional_features=image_data.get("additional_features", {}),
                )
                session.add(new_image)
            await session.commit()


async def main():
    # Confirm the Image table exists in the database
    await ensure_image_table_exists()

    # Read image data from the JSON file
    with open(images_data_file, "r") as file:
        images_data = json.load(file)

    # Populate the database with images
    await insert_images(SessionLocal, images_data)


if __name__ == "__main__":
    asyncio.run(main())
