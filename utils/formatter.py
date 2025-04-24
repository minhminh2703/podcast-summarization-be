from typing import List, Dict, Tuple
#==========================INPUT FORMATTER============================
def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS format, omitting hours/minutes if zero"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    elif minutes > 0:
        return f"{minutes}:{secs:02d}"
    else:
        return f"{secs}"
    
    
def format_sections(segments: List[Dict[str, str]]) -> List[Tuple[str, str]]:
    """
    Format the segments into a structured string for the LLM.
    OUTPUT:
    - List[Tuple[str, str]] - list of tuples with formatted strings for each segment. First element is with start, end; second element is content.
    """
    sentences = []
    for seg in segments:
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip().replace("\n", " ")
        sentences.append(f"[{start} - {end}]: {text}")
    return "\n".join(sentences)
#======================================================================