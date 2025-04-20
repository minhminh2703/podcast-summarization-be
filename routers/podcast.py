from fastapi import APIRouter, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import shutil
from database import get_db
from typing import List
from sqlalchemy.orm import Session
from typing import Dict, Any
from models.podcast import SummarizePodcastURL, PodcastSummarizationResponse, HeadingSection
from schemas.schema import User, PodcastSchema
from utils.whisper import get_whisper_model
from utils.dependencies import auth_middleware
from service.podcast_service import download_audio, transcribe_audio, save_audio_info, save_summarization_heading
from utils.audio import create_audio_name
from service.GPT_service import generate_heading_summary
from utils.GPT import parse_heading_sections, parse_overall_summary

podcast_router = APIRouter(prefix="/podcast", tags=["Podcast"], dependencies=[Depends(auth_middleware)])

@podcast_router.post("/summarize", response_model=PodcastSummarizationResponse)
def summarizeVideoLink(request_data: SummarizePodcastURL, db: Session = Depends(get_db), user: User = Depends(auth_middleware)):
    file_name = create_audio_name(userid=user.userid)
    try:
        audio_path, thumbnail_url, title = download_audio(request_data.URL, 'uploads/', file_name)
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Failed downloading audio: {str(e)}")
    try: 
        transcript, segments, transcribe_time = transcribe_audio(audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed transcribing audio: {str(e)}")
    response_text = generate_heading_summary(segments, request_data.target_language.value)

    headings = parse_heading_sections(response_text)
    overall = parse_overall_summary(response_text)

    audio_schema = save_audio_info(audio_path, title, thumbnail_url, user.userid, request_data.target_language, db)
    save_summarization_heading(headings, audio_schema.id, db)
    
    
    test = PodcastSummarizationResponse(
        title = title,
        thumbnail_url = thumbnail_url,
        detail_summarization = headings,
        overall_summarization = overall
    )
    return test
        

@podcast_router.get("/summarizations", response_model=List[PodcastSummarizationResponse])
def get_all_summarization(
    db: Session = Depends(get_db),
    user: User = Depends(auth_middleware)
):
    podcasts = db.query(PodcastSchema).filter(PodcastSchema.userid == user.userid).all()
    result = []

    for podcast in podcasts:
        # Convert HeadingSectionSchema -> HeadingSection (Pydantic)
        headings = [
            HeadingSection(
                header=section.header,
                title=section.title,
                start=section.start,
                end=section.end,
                content=section.content
            )
            for section in podcast.sections
        ]

        response_item = PodcastSummarizationResponse(
            title=podcast.title,
            thumbnail_url=podcast.thumbnail_url,
            detail_summarization=headings,
            overall_summarization=podcast.summarized_content or ""
        )

        result.append(response_item)

    return result




