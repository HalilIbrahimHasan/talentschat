"""Utility functions for detecting and embedding social media video links"""

import re


def detect_video_url(text):
    """
    Detect video URLs in text and return video info
    Returns: {'type': 'youtube'|'vimeo'|'external', 'video_id': str, 'url': str, 'embed_url': str}
    """
    if not text:
        return None
    
    # YouTube patterns
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in youtube_patterns:
        match = re.search(pattern, text)
        if match:
            video_id = match.group(1)
            return {
                'type': 'youtube',
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'embed_url': f'https://www.youtube.com/embed/{video_id}'
            }
    
    # Vimeo patterns
    vimeo_pattern = r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)'
    match = re.search(vimeo_pattern, text)
    if match:
        video_id = match.group(1)
        return {
            'type': 'vimeo',
            'video_id': video_id,
            'url': f'https://vimeo.com/{video_id}',
            'embed_url': f'https://player.vimeo.com/video/{video_id}'
        }
    
    # Generic video URL (mp4, webm, etc.)
    video_ext_pattern = r'(https?://[^\s]+\.(?:mp4|webm|mov|avi|mkv)(?:\?[^\s]*)?)'
    match = re.search(video_ext_pattern, text, re.IGNORECASE)
    if match:
        return {
            'type': 'external',
            'video_id': None,
            'url': match.group(1),
            'embed_url': match.group(1)
        }
    
    return None


def extract_video_urls(text):
    """Extract all video URLs from text"""
    urls = []
    
    # YouTube
    youtube_pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})'
    for match in re.finditer(youtube_pattern, text):
        video_id = match.group(1)
        urls.append({
            'type': 'youtube',
            'video_id': video_id,
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'embed_url': f'https://www.youtube.com/embed/{video_id}'
        })
    
    # Vimeo
    vimeo_pattern = r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)'
    for match in re.finditer(vimeo_pattern, text):
        video_id = match.group(1)
        urls.append({
            'type': 'vimeo',
            'video_id': video_id,
            'url': f'https://vimeo.com/{video_id}',
            'embed_url': f'https://player.vimeo.com/video/{video_id}'
        })
    
    return urls

