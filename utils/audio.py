from datetime import datetime

def create_audio_name (userid) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{userid}_{timestamp}"  