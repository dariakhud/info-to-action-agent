"""Service for content fetching and processing."""
import logging
from typing import Optional
from src.infra.client.content_fetcher import (
    is_url,
    is_youtube_url,
    fetch_article_text,
    fetch_video_transcript
)
from src.modules.agent.dto import ContentDTO

logger = logging.getLogger(__name__)


class ContentService:
    """Service for fetching and processing content from various sources."""
    
    @staticmethod
    def fetch_content(url: Optional[str] = None, text: Optional[str] = None) -> ContentDTO:
        """
        Fetch content from URL or use provided text.
        
        Args:
            url: URL to fetch content from
            text: Direct text input
            
        Returns:
            ContentDTO with fetched content
            
        Raises:
            ValueError: If content cannot be fetched or is empty
        """
        if url:
            if is_youtube_url(url):
                try:
                    logger.debug(f"Fetching YouTube transcript from: {url}")
                    content_text = fetch_video_transcript(url)
                    source_type = "video transcript"
                except Exception as e:
                    logger.error(f"Failed to fetch video transcript from {url}: {e}", exc_info=True)
                    raise ValueError(f"Failed to fetch video transcript: {e}")
            elif is_url(url):
                try:
                    logger.debug(f"Fetching article from: {url}")
                    content_text = fetch_article_text(url)
                    source_type = "article"
                except Exception as e:
                    logger.error(f"Failed to fetch article from {url}: {e}", exc_info=True)
                    raise ValueError(f"Failed to fetch article: {e}")
            else:
                logger.warning(f"Invalid URL format: {url}")
                raise ValueError("Invalid URL format")
            
            if not content_text:
                logger.warning(f"Empty content extracted from {source_type}: {url}")
                raise ValueError(f"Could not extract text from {source_type}")
            
            return ContentDTO(
                text=content_text,
                source_type=source_type,
                source_url=url
            )
        elif text:
            return ContentDTO(
                text=text,
                source_type="direct text",
                source_url=None
            )
        else:
            raise ValueError("Either url or text must be provided")
