import os
import time
import whisper
from typing import Dict, Any, Optional, Tuple

# Global variable to store the loaded model
_whisper_model = None

def initialize_whisper_model(model_name: str = "base") -> None:
    """
    Initialize the Whisper model during server startup.
    
    Args:
        model_name: The name of the Whisper model to load (default: "base")
    """
    global _whisper_model
    try:
        print(f"Loading Whisper model: {model_name}...")
        start_time = time.time()
        _whisper_model = whisper.load_model(model_name)
        end_time = time.time()
        print(f"Whisper model loaded in {end_time - start_time:.2f} seconds")
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        raise

def get_whisper_model() -> Optional[Any]:
    """
    Get the loaded Whisper model.
    
    Returns:
        The loaded Whisper model or None if not initialized
    """
    return _whisper_model

