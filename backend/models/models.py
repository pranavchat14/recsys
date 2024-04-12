from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    preferences = Column(JSON)  # This will store a list of preferences/tags
    # Add more fields as needed

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    file_path = Column(String, unique=True)  # Path to the image file
    primary_shape = Column(String)
    secondary_shape = Column(String)
    primary_color = Column(String)
    secondary_color = Column(String)
    additional_features = Column(JSON)  # For any other features as a JSON object
    # Define relationships and additional fields as needed

class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    image_id = Column(Integer, ForeignKey('images.id'))

    user = relationship("User", back_populates="likes")
    image = relationship("Image", back_populates="liked_by")

class SavedImage(Base):
    __tablename__ = 'saved_images'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    image_id = Column(Integer, ForeignKey('images.id'))

    user = relationship("User", back_populates="saved_images")
    image = relationship("Image", back_populates="saved_by")

User.likes = relationship("Like", back_populates="user")
User.saved_images = relationship("SavedImage", back_populates="user")
Image.liked_by = relationship("Like", back_populates="image")
Image.saved_by = relationship("SavedImage", back_populates="image")