from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    JSON,
    DateTime,
    ARRAY,
    func,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    preferences = Column(ARRAY(String))  # This will store a list of preferences/tags
    likes = relationship("Like", back_populates="user")
    saved_images = relationship("SavedImage", back_populates="user")
    # Add more fields as needed


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String, unique=True)  # Path to the image file
    primary_shape = Column(String)
    secondary_shape = Column(String)
    primary_color = Column(String)
    secondary_color = Column(String)
    tags = Column(ARRAY(String))
    additional_features = Column(JSON)  # For any other features as a JSON object
    liked_by = relationship("Like", back_populates="image")
    saved_by = relationship("SavedImage", back_populates="image")

    @hybrid_property
    def popularity_score(self):
        return len(self.liked_by) + len(self.saved_by)


class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_id = Column(Integer, ForeignKey("images.id"))
    created_at = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Tracks when the like was made

    user = relationship("User", back_populates="likes")
    image = relationship("Image", back_populates="liked_by")


class SavedImage(Base):
    __tablename__ = "saved_images"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_id = Column(Integer, ForeignKey("images.id"))

    user = relationship("User", back_populates="saved_images")
    image = relationship("Image", back_populates="saved_by")


class UserFeed(Base):
    __tablename__ = "user_feeds"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    recommended_image_ids = Column(ARRAY(Integer))
    user = relationship("User")
