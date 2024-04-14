from typing import List
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, ARRAY
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime, timedelta

from .utils import calculate_similarity
from ..models.models import Image, User, Like  # Importing necessary models

class RecommendationEngine:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    async def get_liked_images(self, user_id: int) -> List[Image]:
        async with self.db_session_factory() as session:
            stmt = select(Like).where(Like.user_id == user_id)
            result = await session.execute(stmt)
            likes = result.scalars().all()
            liked_images = [like.image for like in likes]  # Retrieve 'image' attribute directly
            return liked_images

    async def get_trending_images(self, days: int = 7) -> List[Image]:
        trend_start_date = datetime.now() - timedelta(days=days)
        async with self.db_session_factory() as session:  # Use session factory correctly
            stmt = (
                select(Image).join(Like, Like.image_id == Image.id)
                .filter(Like.created_at >= trend_start_date)
                .group_by(Image.id)
                .order_by(func.count(Like.id).desc())
                .limit(10)
            )
            result = await session.execute(stmt)
            await session.commit()  # Ensure changes are committed
            trending_images = result.scalars().all()  # Fetch all results at once
            return trending_images

    async def recommend_images_collaborative(self, user_id: int) -> List[Image]:
        async with self.db_session_factory() as session:
            interactions_query = await session.execute(select(Like))
            interactions = interactions_query.scalars().all()  # Fetch all interactions directly
            user_ids = list(set([interaction.user_id for interaction in interactions]))
            image_ids = list(set([interaction.image_id for interaction in interactions]))
            user_item_matrix = np.zeros((len(user_ids), len(image_ids)))
            for interaction in interactions:
                user_index = user_ids.index(interaction.user_id)
                image_index = image_ids.index(interaction.image_id)
                user_item_matrix[user_index, image_index] = 1
            similarity_scores = cosine_similarity(user_item_matrix)
            try:
                user_index = user_ids.index(user_id)
                user_scores = similarity_scores[user_index]
            except ValueError:
                return []
            similar_users_indices = np.argsort(-user_scores)[1:6]
            recommended_items = set()
            for idx in similar_users_indices:
                user_interactions = np.where(user_item_matrix[idx] > 0)[0]
                recommended_items.update(user_interactions)
            recommended_images = [
                (await session.execute(select(Image).filter(Image.id == image_ids[idx]))).scalars().first()
                for idx in recommended_items
            ]
            return recommended_images

    async def recommend_images_hybrid(self, user_id: int) -> List[Image]:
        async with self.db_session_factory() as session:
            user = await session.get(User, user_id)
            if not user or not user.preferences:
                return []
            preferred_images_query = select(
                Image.id, Image.title, Image.url, Image.primary_shape, Image.secondary_shape, 
                Image.primary_color, Image.secondary_color, Image.tags, Image.additional_features
            ).where(Image.tags.op('&&')(user.preferences))
            preferred_images_result = await session.execute(preferred_images_query)
            preferred_images = preferred_images_result.scalars().all()
            liked_images = await self.get_liked_images(user_id)
            refined_recommendations = set()
            for preferred_image in preferred_images:
                for liked_image in liked_images:
                    similarity = calculate_similarity(preferred_image.file_path, liked_image.file_path)
                    if similarity > 0.5:
                        refined_recommendations.add(preferred_image)
                        break
            return list(refined_recommendations)

    async def comprehensive_recommendation(self, user_id: int) -> List[Image]:
        liked_images = await self.get_liked_images(user_id)
        trending_images = await self.get_trending_images()
        collaborative_images = await self.recommend_images_collaborative(user_id)
        hybrid_images = await self.recommend_images_hybrid(user_id)
        
        # Combine all recommendations into a unique set to avoid duplicates
        all_recommended_images = set(liked_images + trending_images + collaborative_images + hybrid_images)
        
        # Convert the set back to a list before returning
        return list(all_recommended_images)

