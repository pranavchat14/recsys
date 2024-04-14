from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.exc import IntegrityError
from ..database.database import engine
from typing import List

from ..crud import crud_user
from ..models.models import User, Base
from ..schemas.user import UserCreate, UserUpdate, User as UserSchema

from ..crud import crud_image
from ..models.models import Image, Like, SavedImage
from ..schemas.image import ImageCreate, Image as ImageSchema

from .dependencies import get_db
from ..core.security import get_password_hash

from ..recommendations.recommendation_engine import RecommendationEngine
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Use Base.metadata.create_all to create your tables
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Here you can add shutdown logic if needed


app = FastAPI(lifespan=app_lifespan)

# Initialize RecommendationEngine once for reuse, passing the database session
recommendation_engine = RecommendationEngine(db_session_factory=get_db)

@app.post("/users/", response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user_by_email = await crud_user.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user_by_username = await crud_user.get_user_by_username(
        db, username=user.username
    )
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    return await crud_user.create_user(db=db, user=new_user)


@app.get("/users/{user_id}", response_model=UserSchema)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = await crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=UserSchema)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    user_data = user.model_dump(exclude_unset=True)

    if "password" in user_data:
        hashed_password = get_password_hash(user_data["password"])
        user_data["hashed_password"] = hashed_password
        del user_data["password"]  # Remove the plain 'password' field

    return await crud_user.update_user(db, user_id, user_data)


@app.delete("/users/{user_id}", response_model=UserSchema)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    async with db as session:
        async with session.begin():
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            try:
                user_to_delete = result.scalar_one()
            except NoResultFound:
                raise HTTPException(status_code=404, detail="User not found")

            await session.delete(user_to_delete)
            await session.commit()

            return user_to_delete


@app.post("/images/", response_model=ImageSchema)
async def create_image(image: ImageCreate, db: Session = Depends(get_db)):
    new_image = Image(title=image.title, url=image.url)
    return await crud_image.create_image(db=db, image=new_image)


@app.get("/images/{image_id}", response_model=ImageSchema)
async def read_image(image_id: int, db: Session = Depends(get_db)):
    db_image = await crud_image.get_image(db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return db_image


@app.put("/images/{image_id}", response_model=ImageSchema)
async def update_image(image_id: int, image_data: dict, db: Session = Depends(get_db)):
    return await crud_image.update_image(db, image_id, image_data)


@app.delete("/images/{image_id}", response_model=ImageSchema)
async def delete_image(image_id: int, db: Session = Depends(get_db)):
    async with db as session:
        async with session.begin():
            stmt = select(Image).where(Image.id == image_id)
            result = await session.execute(stmt)
            try:
                image_to_delete = result.scalar_one()
            except NoResultFound:
                raise HTTPException(status_code=404, detail="Image not found")

            await session.delete(image_to_delete)
            await session.commit()

            return image_to_delete


@app.post("/images/{image_id}/like/")
async def like_image(image_id: int, user_id: int, db: Session = Depends(get_db)):
    new_like = Like(user_id=user_id, image_id=image_id)
    db.add(new_like)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return {"msg": "You already liked this image"}
    return {"msg": "Image liked successfully"}


@app.post("/images/{image_id}/save/")
async def save_image(user_id: int, image_id: int, db: Session = Depends(get_db)):
    new_saved_image = SavedImage(user_id=user_id, image_id=image_id)
    db.add(new_saved_image)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return {"msg": "Image already saved"}
    return {"msg": "Image saved successfully"}


@app.get("/images/trending/", response_model=List[ImageSchema])
async def read_trending_images(db: Session = Depends(get_db), days: int = 7):
    trending_images = await recommendation_engine.get_trending_images(days=days)
    if not trending_images:
        raise HTTPException(status_code=404, detail="No trending images found")
    return trending_images


@app.post("/users/{user_id}/preferences/")
async def update_user_preferences(
    user_id: int, preferences: List[str], db: Session = Depends(get_db)
):
    user = await crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.preferences = preferences
    db.add(user)
    await db.commit()
    return {"msg": "Preferences updated successfully"}

@app.get("/users/{user_id}/recommendations/", response_model=List[ImageSchema])
async def get_image_recommendations(user_id: int, db: Session = Depends(get_db)):
    try:
        # Fetch comprehensive recommendations
        comprehensive_images = await recommendation_engine.comprehensive_recommendation(user_id=user_id)
        if not comprehensive_images:
            raise HTTPException(status_code=404, detail="No recommendations available")
        return comprehensive_images
    except Exception as e:
        # Output error to console and log it for further investigation
        print(f'Error occurred: {e}')
        logger.error(f"Error fetching comprehensive image recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recommendations due to an internal error")
