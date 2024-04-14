from backend.database.database import SessionLocal
from backend.recommendations.recommendation_engine import RecommendationEngine
from backend.app.dependencies import get_db
# Test the recommendation functions

recommendation_engine = RecommendationEngine(db=get_db)
user_id = 1  # Replace with a valid user ID for testing

async def main():
    liked_images = await recommendation_engine.get_liked_images(user_id)
    print(liked_images)

# Run the async function
import asyncio
asyncio.run(main())