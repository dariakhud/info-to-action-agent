"""Service for AI operations (summarization, action extraction)."""
import logging
from src.infra.client.google_client import get_genai_client

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered text processing."""
    
    @staticmethod
    def summarize_text(text: str) -> str:
        """
        Summarizes text into 5 key bullet points using Gemini API.
        
        Args:
            text: Text to summarize
            
        Returns:
            Summary as markdown formatted string
        """
        logger.debug(f"Summarizing text ({len(text)} characters)")
        try:
            client = get_genai_client()
            response = client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents='Summarize the following text into exactly 5 concise bullet points:\n\n' + text
            )
            logger.debug("Text summarized successfully")
            return response.text
        except Exception as e:
            logger.error(f"Failed to summarize text: {e}", exc_info=True)
            raise
    
    @staticmethod
    def extract_actions(summary: str) -> list[str]:
        """
        Extracts 3-5 concrete actionable tasks from summary points.
        
        Args:
            summary: Summary text to extract actions from
            
        Returns:
            List of actionable tasks
        """
        logger.debug("Extracting actions from summary")
        try:
            client = get_genai_client()
            response = client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents='Given these summary points, extract 3 to 5 concrete, actionable tasks for a calendar. Return ONLY a simple list, one per line:\n\n' + summary
            )
            # Basic parsing: split by lines and filter empty/index markers
            actions = [line.strip().lstrip('- 12345. ') for line in response.text.split('\n') if line.strip()]
            logger.debug(f"Extracted {len(actions[:5])} actions")
            return actions[:5]
        except Exception as e:
            logger.error(f"Failed to extract actions: {e}", exc_info=True)
            raise
