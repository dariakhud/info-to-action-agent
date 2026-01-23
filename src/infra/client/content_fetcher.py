"""Content fetching clients (HTTP, YouTube)."""
import logging
import re
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)


def is_url(input_str: str) -> bool:
    """Simple check if a string is a URL."""
    return input_str.strip().startswith(('http://', 'https://'))


def is_youtube_url(url: str) -> bool:
    """Detects if a URL is a YouTube link."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return bool(re.match(youtube_regex, url))


def fetch_article_text(url: str) -> str:
    """Fetches the main text from an online article URL."""
    logger.debug(f"Fetching article: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"HTTP error fetching article {url}: {e}", exc_info=True)
        raise
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style", "nav", "header", "footer", "aside"]):
        script_or_style.decompose()

    # Try to find common article tags
    article = soup.find('article')
    if not article:
        # Fallback to main or specific containers if article tag is missing
        article = soup.find('main') or soup.find('div', class_=re.compile(r'article|post|content|entry', re.I))
    
    # If still not found, use body
    if not article:
        article = soup.body
        
    if not article:
        return ""

    # Get text from paragraphs
    paragraphs = article.find_all('p')
    text = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
    
    return text.strip()


def fetch_video_transcript(url: str) -> str:
    """Extracts the transcript text from a YouTube video URL."""
    logger.debug(f"Fetching YouTube transcript: {url}")
    # Extract video ID from URL
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
    if not video_id_match:
        logger.error(f"Could not extract video ID from URL: {url}")
        raise ValueError("Could not extract YouTube video ID from URL")
    
    video_id = video_id_match.group(1)
    logger.debug(f"Extracted video ID: {video_id}")
    api = YouTubeTranscriptApi()
    
    # Try to get English transcripts first
    try:
        transcript_data = api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
        logger.debug("Fetched English transcript")
    except Exception:
        # Fallback: list all and take the first one available
        logger.debug("English transcript not available, trying fallback")
        try:
            transcript_list = api.list(video_id)
            transcript = next(iter(transcript_list))
            transcript_data = transcript.fetch()
            logger.debug(f"Fetched transcript in alternative language")
        except Exception as e:
            logger.error(f"No transcripts found for video {video_id}: {e}", exc_info=True)
            raise ValueError(f"No transcripts found for this video: {e}")
    
    # Join transcript parts into a single string
    text = ' '.join([item.text for item in transcript_data])
    logger.debug(f"Transcript extracted: {len(text)} characters")
    return text.strip()
