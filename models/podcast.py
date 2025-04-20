from pydantic import BaseModel
from enum import Enum
from uuid import UUID
from typing import List


class TargetLanguage(Enum):
    EN = "English"
    VI = "Vietnamese"

class SummarizePodcastURL(BaseModel):
    URL: str
    target_language: TargetLanguage

class HeadingSection(BaseModel):
    header: str
    title: str
    start: float
    end: float
    content: str


class PodcastSummarizationResponse(BaseModel):
    detail_summarization: List[HeadingSection]
    thumbnail_url: str
    title: str
    overall_summarization: str
