"""YouTube URL parsing utilities"""
import re


def extract_youtube_id(url):
    """
    Extract YouTube video ID from various YouTube URL formats.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID
    - VIDEO_ID (if already just an ID)
    
    Returns the video ID or None if not found.
    """
    if not url:
        return None
    
    # If it's already just an ID (11 characters, alphanumeric, dashes, underscores)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url.strip()):
        return url.strip()
    
    # Pattern for youtube.com/watch?v=VIDEO_ID
    match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})', url)
    if match:
        return match.group(1)
    
    return None


def get_youtube_embed_url(youtube_id):
    """Generate YouTube embed URL from video ID"""
    if not youtube_id:
        return None
    return f"https://www.youtube.com/embed/{youtube_id}"




