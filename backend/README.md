# Backend Service for Image Management and Recommendation

This backend service is designed to manage a collection of images and provide recommendations based on user preferences. It includes scripts for inserting images into the database, generating images with specific features, and recommending images to users.

## Key Components

- **Image Generation**: Utilizes `backend/scripts/generate_images.py` to create images with specified features such as shapes and colors, and saves them along with their metadata.
- **Database Management**: Uses `backend/scripts/insert_images_to_db.py` to insert generated images into the database, ensuring the `Image` table exists and is populated with the image data.
- **Recommendation Engine**: Leverages `backend/recommendations/recommendation_engine.py` to recommend images to users based on their preferences stored in the database. This includes comprehensive recommendations that combine various recommendation strategies.
- **Similarity Calculation**: Implements a utility in `backend/recommendations/utils.py` to calculate the similarity between images, which can be used to refine recommendations.
- **API Endpoints**: Defined in `backend/app/main.py`, providing interfaces for user management, image CRUD operations, fetching recommended images, and updating user preferences.

## Setup and Execution

1. **Ensure Python and necessary libraries are installed**: The project requires Python 3.8+ and libraries such as FastAPI, SQLAlchemy, and PIL.

2. **Database Setup**: Configure the database connection in `backend/database/database.py`. The project uses an asynchronous SQLAlchemy session for database interactions.

3. **Generate Images**: Run `python backend/scripts/generate_images.py` to generate images and save their data in a JSON file.

4. **Populate Database**: Execute `python backend/scripts/insert_images_to_db.py` to create the `Image` table (if it doesn't exist) and populate it with the generated image data.

5. **Start the FastAPI server**: Launch the backend service by running `uvicorn backend.app.main:app --reload`. The API documentation will be available at `http://127.0.0.1:8000/docs`.

6. **Interact with the API**: Use the provided endpoints to create users, upload images, get image recommendations, and update user preferences.

## Future Enhancements

- **Image Tagging**: Implement automatic tagging of images based on their features to improve recommendation accuracy.
- **User Feedback Loop**: Incorporate user feedback on recommendations to refine the recommendation engine.
- **Performance Optimization**: Explore ways to optimize image similarity calculations for larger datasets.
- **User Feed**: Develop a personalized user feed that dynamically updates based on user interactions and preferences.

