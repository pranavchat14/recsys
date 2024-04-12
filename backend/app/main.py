from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database.database import SessionLocal, engine
from typing import List

from ..crud import crud_user
from ..models.models import User, Base
from ..schemas.user import UserCreate, User as UserSchema

from ..crud import crud_image
from ..models.models import Image, Like, SavedImage
from ..schemas.image import ImageCreate, Image as ImageSchema

from .dependencies import get_db
from ..core.security import get_password_hash

from ..recommendations.recommendation_engine import recommend_images

app = FastAPI()

# Define the async function to create tables
async def create_tables():
    async with engine.begin() as conn:
        # Use Base.metadata.create_all to create your tables
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def startup_event():
    # Call the create_tables function at startup
    await create_tables()

@app.post("/users/", response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = await crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user = User(
       username=user.username,
       email=user.email,
       hashed_password=hashed_password
    ) 
    return await crud_user.create_user(db=db, user=user)

@app.get("/users/{user_id}", response_model=UserSchema)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = await crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=UserSchema)
async def update_user(user_id: int, user_data: dict, db: Session = Depends(get_db)):
    return await crud_user.update_user(db, user_id, user_data)

@app.delete("/users/{user_id}", response_model=UserSchema)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    return await crud_user.delete_user(db, user_id)


@app.post("/images/", response_model=ImageSchema)
async def create_image(image: ImageCreate, db: Session = Depends(get_db)):
    db_image = await crud_image.get_image_by_title(db, title=image.title)
    if db_image:
        raise HTTPException(status_code=400, detail="Image with this title already exists")
    
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
    return await crud_image.delete_image(db, image_id)

@app.post("/users/{user_id}/preferences/")
async def update_user_preferences(user_id: int, preferences: List[str], db: Session = Depends(get_db)):
    user = await crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.preferences = preferences
    db.add(user)
    await db.commit()
    return {"msg": "Preferences updated successfully"}

@app.get("/users/{user_id}/recommendations/", response_model=List[ImageSchema])
async def get_image_recommendations(user_id: int, db: Session = Depends(get_db)):
    images = recommend_images(user_id, db)
    if not images:
        raise HTTPException(status_code=404, detail="No recommendations found")
    return images

@app.post("/images/{image_id}/like/")
async def like_image(user_id: int, image_id: int, db: Session = Depends(get_db)):
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