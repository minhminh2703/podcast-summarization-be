from fastapi import APIRouter, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import shutil
from database import get_db
from typing import List
from sqlalchemy.orm import Session
from models.podcast import SummarizePodcastURL, PodcastSummarizationResponse, HeadingSection, GetAllPodcastSummarizationResponse, GetSinglePodcastSummarizationResponse
from schemas.schema import User, PodcastSchema
from utils.dependencies import auth_middleware
from sqlalchemy.orm.exc import NoResultFound
from service.podcast_service import download_audio, transcribe_audio, save_audio_info, save_summarization_heading
from utils.audio import create_audio_name
from service.GPT_service import generate_heading_summary
from utils.GPT import parse_headings_and_overall

podcast_router = APIRouter(prefix="/podcast", tags=["Podcast"], dependencies=[Depends(auth_middleware)])

@podcast_router.post("/summarize", response_model=PodcastSummarizationResponse)
def summarizeVideoLink(request_data: SummarizePodcastURL, db: Session = Depends(get_db), user: User = Depends(auth_middleware)):
    file_name = create_audio_name(userid=user.userid)
    try:
        audio_path, thumbnail_url, title, audio_type = download_audio(request_data.URL, 'uploads/', file_name)
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Failed downloading audio: {str(e)}")
    try: 
        transcript, segments, transcribe_time = transcribe_audio(audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed transcribing audio: {str(e)}")
    response_text = generate_heading_summary(segments, request_data.target_language.value)
    print ("GPT Response: ", response_text)

    headings, overall = parse_headings_and_overall(response_text)

    podcast_shcema = save_audio_info(audio_type ,request_data.URL, audio_path, title, thumbnail_url, user.userid, request_data.target_language, db, overall)
    save_summarization_heading(headings, podcast_shcema.id, db)
    
    
    test = PodcastSummarizationResponse(
        podcast_id= podcast_shcema.id,
        title = title,
        thumbnail_url = thumbnail_url,
        detail_summarization = headings,
        overall_summarization = overall,
        created_at= podcast_shcema.created_at
    )
    return test
        

@podcast_router.get("/summarizations", response_model=List[GetAllPodcastSummarizationResponse])
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

        response_item = GetAllPodcastSummarizationResponse(
            podcast_id=podcast.id,
            title=podcast.title,
            thumbnail_url=podcast.thumbnail_url,
            created_at= podcast.created_at,
            language=podcast.target_language
        )

        result.append(response_item)

    return result


@podcast_router.get("/summarizations/{podcast_id}", response_model=GetSinglePodcastSummarizationResponse)
def get_single_summarization(
    podcast_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(auth_middleware)
):
    try:
        podcast = db.query(PodcastSchema).filter(
            PodcastSchema.userid == user.userid,
            PodcastSchema.id == podcast_id
            ).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Podcast not found")

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

    response = GetSinglePodcastSummarizationResponse(
        podcast_id=podcast.id,
        title=podcast.title,
        thumbnail_url=podcast.thumbnail_url,
        detail_summarization = headings,
        overall_summarization = podcast.summarized_content,    
        created_at= podcast.created_at,
        language= podcast.target_language,
        podcast_url=podcast.podcast_url,
        podcast_type=podcast.podcast_type
    )

    return response

