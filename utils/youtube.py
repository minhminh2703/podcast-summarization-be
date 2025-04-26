import os
from urllib.parse import urlparse, parse_qs
from typing import Tuple
from yt_dlp import YoutubeDL


# ========================
# Get YouTube Thumbnail URL
# ========================
def get_youtube_thumbnail_url(video_url: str) -> str:
    parsed_url = urlparse(video_url)
    video_id = None

    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query = parse_qs(parsed_url.query)
        video_id = query.get("v", [None])[0]
    elif parsed_url.hostname == "youtu.be":
        video_id = parsed_url.path.lstrip("/")

    if video_id:
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    else:
        raise ValueError("Invalid YouTube URL, cannot extract video ID.")


# ========================
# Download YouTube video
# ========================
def download_single_youtube_video(video_url: str, output_path: str, file_name: str) -> Tuple[str, str, str]:
    try:
        os.makedirs(output_path, exist_ok=True)

        target_path = os.path.join(output_path, file_name + '.%(ext)s')

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': target_path,
            'ignoreerrors': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            if not info:
                raise RuntimeError("Failed to extract video info.")
            title = info.get('title') or file_name
            video_path = os.path.join(output_path, f"{file_name}.mp3")
            thumbnail_url = get_youtube_thumbnail_url(video_url)
            return video_path, thumbnail_url, title, 'youtube'
    except Exception as e:
        raise RuntimeError(f"Download from YouTube failed: {str(e)}")
