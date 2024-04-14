import pytest
from backend.recommendations.recommendation_engine import generate_recommendations
from backend.tests.test_database import db_session


@pytest.mark.asyncio
async def test_generate_recommendations(db_session):
    # Assuming generate_recommendations takes a user_id and db_session
    recommendations = await generate_recommendations(user_id=1, db=db_session)
    assert isinstance(recommendations, list)
