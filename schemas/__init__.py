# models/__init__.py
from sqlalchemy.ext.declarative import declarative_base
from schemas.schema import PodcastSchema

Base = declarative_base()

__all__ = ["User", "PodcastSchema", "HeadingSectionSchema"]
