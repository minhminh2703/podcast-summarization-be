import time
import torch
import whisper
from typing import Tuple

# Choose the whisper model size based on your needs and resources
# Options: "tiny", "base", "small", "medium", "large"
WHISPER_MODEL_SIZE = "tiny"

# Load the model (it will be downloaded the first time)
def load_whisper_model():
    """Load and return the Whisper model"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model = whisper.load_model(WHISPER_MODEL_SIZE, device=device)
    return model

# Cache the model to avoid reloading
_whisper_model = None

def get_whisper_model():
    """Get the cached Whisper model or load it if not available"""
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = load_whisper_model()
    return _whisper_model

def transcribe_audio(audio_path: str) -> Tuple[str, float]:
    """
    Transcribe audio file using Whisper model.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Tuple of (transcription text, audio duration in seconds)
    """
    start_time = time.time()
    model = get_whisper_model()
    
    # Transcribe the audio
    result = model.transcribe(audio_path)
    
    # Calculate processing time for monitoring
    processing_time = time.time() - start_time
    print(f"Audio transcription completed in {processing_time:.2f} seconds")
    
    return result["text"], result.get("duration", 0)