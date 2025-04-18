# backend/app.py
import os
import time
import tempfile
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our model wrappers
from models.whisper_model import transcribe_audio
from models.summarizer import generate_summary

app = FastAPI(title="Podcast Summarizer API")

# Add CORS middleware to allow requests from the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def safe_delete(path, retries=3, delay=0.5):
    for _ in range(retries):
        try:
            os.unlink(path)
            return
        except PermissionError:
            time.sleep(delay)


class SummaryResponse(BaseModel):
    transcription: str
    summary: str
    duration: float

@app.get("/")
def read_root():
    return {"status": "active", "message": "Podcast Summarizer API is running"}

@app.post("/summarize", response_model=SummaryResponse)
async def summarize_podcast(
    file: UploadFile = File(...),
    summarization_type: str = Form("concise"),  # concise, detailed, or bullets
    max_summary_length: Optional[int] = Form(300)
):
    """
    Process an uploaded podcast audio file:
    1. Transcribe using Whisper
    2. Summarize using GPT and LangChain
    """
    if not file.filename.endswith(('.mp3', '.mp4', '.wav', '.m4a')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name
        
        # Transcribe the audio using Whisper
        transcription, duration = transcribe_audio(temp_file_path)

        if not transcription:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")
        
        # Generate summary using GPT
        summary = generate_summary(
            transcription, 
            summary_type=summarization_type,
            max_length=max_summary_length
        )
        
        # Delete the temporary file
        safe_delete(temp_file_path)

        return SummaryResponse(
            transcription=transcription,
            summary=summary,
            duration=duration
        )
    
    except Exception as e:
        # Ensure the temp file is deleted in case of error
        if 'temp_file_path' in locals():
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing podcast: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)