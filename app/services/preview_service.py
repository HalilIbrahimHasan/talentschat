import re
from urllib.parse import urlparse


def extract_urls(text):
    """Extract URLs from text"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)


def get_link_preview(url):
    """Get basic link preview (title only for MVP)"""
    # For MVP, just return the domain
    # In production, you could use libraries like requests + BeautifulSoup
    try:
        parsed = urlparse(url)
        return {
            'url': url,
            'domain': parsed.netloc,
            'title': parsed.netloc  # Placeholder
        }
    except:
        return None




