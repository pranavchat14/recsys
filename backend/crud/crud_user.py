from sqlalchemy.future import select
from ..models.models import User

async def get_user(db, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db, user: User):
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user(db, user_id: int, user_data: dict):
    await db.execute(User.__table__.update().where(User.id == user_id).values(user_data))
    await db.commit()
    return await get_user(db, user_id)

async def delete_user(db, user_id: int):
    user = await get_user(db, user_id)
    db.delete(user)
    await db.commit()
    return user