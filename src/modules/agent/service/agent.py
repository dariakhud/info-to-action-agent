"""Main agent service orchestrating the workflow."""
import logging
from typing import Optional
from src.modules.agent.service.content import ContentService
from src.modules.agent.service.ai import AIService
from src.modules.agent.service.calendar import CalendarService
from src.modules.agent.dto import ContentDTO, SummaryDTO, ActionDTO

logger = logging.getLogger(__name__)


class AgentService:
    """Main service orchestrating the information-to-action workflow."""
    
    def __init__(self):
        self.content_service = ContentService()
        self.ai_service = AIService()
        self.calendar_service = CalendarService()
    
    def process_content(
        self,
        url: Optional[str] = None,
        text: Optional[str] = None
    ) -> ContentDTO:
        """
        Process and fetch content from URL or text.
        
        Args:
            url: URL to fetch content from
            text: Direct text input
            
        Returns:
            ContentDTO with processed content
        """
        if url:
            logger.info(f"Processing content from URL: {url}")
        else:
            logger.info("Processing direct text input")
        
        try:
            content = self.content_service.fetch_content(url=url, text=text)
            logger.info(f"Content processed: {len(content.text)} characters from {content.source_type}")
            return content
        except Exception as e:
            logger.error(f"Failed to process content: {e}", exc_info=True)
            raise
    
    def summarize(self, content: ContentDTO) -> SummaryDTO:
        """
        Summarize content into key points.
        
        Args:
            content: ContentDTO to summarize
            
        Returns:
            SummaryDTO with summary points
        """
        logger.info(f"Summarizing content ({len(content.text)} characters)")
        try:
            summary_text = self.ai_service.summarize_text(content.text)
            summary = SummaryDTO(
                points=summary_text,
                source_type=content.source_type,
                character_count=len(content.text)
            )
            logger.info("Content summarized successfully")
            return summary
        except Exception as e:
            logger.error(f"Failed to summarize content: {e}", exc_info=True)
            raise
    
    def extract_actions(self, summary: SummaryDTO) -> list[str]:
        """
        Extract actionable tasks from summary.
        
        Args:
            summary: SummaryDTO to extract actions from
            
        Returns:
            List of actionable tasks
        """
        logger.info("Extracting actions from summary")
        try:
            actions = self.ai_service.extract_actions(summary.points)
            logger.info(f"Extracted {len(actions)} actions")
            return actions
        except Exception as e:
            logger.error(f"Failed to extract actions: {e}", exc_info=True)
            raise
    
    def schedule_action(self, action: str, start_time, duration_hours: int = 1):
        """
        Schedule an action in Google Calendar.
        
        Args:
            action: Action description
            start_time: Start time for the event
            duration_hours: Duration in hours
            
        Returns:
            ScheduledEventDTO with event details
        """
        logger.info(f"Scheduling action: '{action}' for {start_time}")
        try:
            event = self.calendar_service.add_event(action, start_time, duration_hours)
            logger.info(f"Action scheduled successfully: {event.event_link}")
            return event
        except Exception as e:
            logger.error(f"Failed to schedule action '{action}': {e}", exc_info=True)
            raise
