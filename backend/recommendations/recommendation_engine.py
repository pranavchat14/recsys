from typing import List
from sqlalchemy.orm import Session
from ..models.models import Image, User

def recommend_images(user_id: int, db: Session) -> List[Image]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.preferences:
        return []

    # Fetch images that match any of the user's preferences
    preferred_images = db.query(Image).filter(Image.tags.any(user.preferences)).all()
    return preferred_images