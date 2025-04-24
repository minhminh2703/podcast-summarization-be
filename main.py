from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers.auth import auth_router
from routers.podcast import podcast_router
from routers.user import user_router
from database import init_db
from utils.whisper import initialize_whisper_model
import signal
import sys
import os

# Flag to track if we're shutting down
is_shutting_down = False

def signal_handler(sig, frame):
    global is_shutting_down
    if not is_shutting_down:
        is_shutting_down = True
        print("Shutting down successfully...")
        os._exit(0)

signal.signal(signal.SIGINT, signal_handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        initialize_whisper_model(model_name="tiny")
        # initialize_whisper_model(model_name="turbo")
    except Exception as e:
        print(f"Failed to initialize Whisper model: {e}")
    
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(auth_router)
app.include_router(podcast_router)
app.include_router(user_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
    # from utils.segmentation import initialize_mini_llm
    # from utils.segmentation import initialize_miniLM, minilm_topic_segmentation, initialize_embedder
    # initialize_embedder(model_name="all-MiniLM-L6-v2")
    # initialize_whisper_model(model_name="tiny")
    # from service.podcast_service import transcribe_audio
    # audio_path = r"C:\Users\ACER\Downloads\ricardo_vargas_2025_04_14_negotiation_stuck_en.mp3"
    # transcript, segment, transcribe_time = transcribe_audio(audio_path)
    # from service.GPT_service import generate_summary
    # summary = generate_summary(segment, target_language="English")
    # print(summary)