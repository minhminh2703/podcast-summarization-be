import re
import requests
import feedparser
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from typing import Tuple


# ========================
# Download podcast from RSS
# ========================
def download_RSS(rss_url: str, local_path: str, file_name: str) -> Tuple[str, str, str]:
    try:
        feed = feedparser.parse(rss_url)
        if 'feed' not in feed or not feed.entries:
            raise ValueError("RSS feed is empty or invalid.")

        episode = feed.entries[0]
        episode_title = episode.get('title', 'Untitled Episode')
        thumbnail_url = feed['feed'].get('image', {}).get('href', '')

        audio_url = next((link.href for link in episode.links if link.type == 'audio/mpeg'), None)
        if not audio_url:
            raise ValueError("No audio/mpeg URL found in RSS.")

        audio_path = Path(local_path) / f"{file_name}.mp3"

        with requests.get(audio_url, stream=True) as r:
            r.raise_for_status()
            with open(audio_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        return str(audio_path), thumbnail_url, episode_title, 'RSS'

    except Exception as e:
        raise RuntimeError(f"Download from RSS failed: {str(e)}")
