from sqlalchemy import Column, String, Float, ForeignKey, Text, TIMESTAMP, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    userid = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    profile_picture = Column(LargeBinary, nullable=True)
    
    # Relationship with Podcast
    podcasts = relationship("PodcastSchema", back_populates="user")

class PodcastSchema(Base):
    __tablename__ = "podcasts"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    userid = Column(String(36), ForeignKey("users.userid", ondelete="CASCADE"), nullable=False)
    thumbnail_url = Column(String(255), nullable=True)
    audio_path = Column(String(255), nullable=False)
    summarized_content = Column(Text, nullable=True)
    target_language = Column(String(50), nullable=True)
    duration = Column(Float, nullable=True)

    user = relationship("User", back_populates="podcasts")  # ✅ tên class phải đúng
    sections = relationship("HeadingSectionSchema", back_populates="podcast", cascade="all, delete-orphan", passive_deletes=True)


class HeadingSectionSchema(Base):
    __tablename__ = "heading_section"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    header = Column(String(255), nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    start = Column(Float, nullable=False)
    end = Column(Float, nullable=False)
    podcast_id = Column(String(36), ForeignKey("podcasts.id", ondelete="CASCADE"), nullable=False)

    podcast = relationship("PodcastSchema", back_populates="sections")
