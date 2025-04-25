import os
import re
import time
import requests
import feedparser
import whisper
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from typing import Tuple
from yt_dlp import YoutubeDL
from utils.youtube import download_single_youtube_video
from utils.RSS import download_RSS
from utils.whisper import get_whisper_model
from models.podcast import TargetLanguage
from sqlalchemy.orm import Session
from schemas.schema import PodcastSchema
from typing import List
from models.podcast import HeadingSection
from schemas.schema import HeadingSectionSchema
import uuid

# ========================
# Unified download handler
# ========================
def download_audio(link: str, output_path: str, file_name: str) -> Tuple[str, str, str]:
    try:
        os.makedirs(output_path, exist_ok=True)
        if "youtube.com" in link or "youtu.be" in link:
            return download_single_youtube_video(link, output_path, file_name)
        else:
            return download_RSS(link, output_path, file_name)
    except Exception as e:
        raise RuntimeError(f"Download failed: {str(e)}")

def transcribe_audio(audio_path: str) -> Tuple[str, list[str], float]:
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        start = time.time()
        model = get_whisper_model()
        result = model.transcribe(audio_path)
        transcript = result["text"]
        segment = result["segments"]
        transcribe_time = time.time() - start
        return transcript, segment, transcribe_time
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {str(e)}")
    
def save_audio_info(
    audio_path: str,
    title: str,
    thumbnail_url: str,
    userid: str,
    targetLanguage: TargetLanguage, 
    db: Session,
    overallSummarization: str,
) -> PodcastSchema:
    new_podcast = PodcastSchema(
        title=title,
        userid=userid,
        thumbnail_url=thumbnail_url,
        target_language=targetLanguage.value,
        audio_path=audio_path,
        duration=0,
        summarized_content= overallSummarization
    )

    db.add(new_podcast)
    db.commit()
    db.refresh(new_podcast)  

    return new_podcast


def save_summarization_heading(input: List[HeadingSection], podcast_id: str, db: Session):
    for section in input:
        new_section = HeadingSectionSchema(
            id=str(uuid.uuid4()),
            header=section.header,
            title=section.title,
            content=section.content,
            start=section.start,
            end=section.end,
            podcast_id=podcast_id
        )
        db.add(new_section)

    db.commit()
    
