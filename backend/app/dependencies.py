from ..database.database import SessionLocal


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
