"""Main agent service orchestrating the workflow."""
from typing import Optional
from src.modules.agent.service.content import ContentService
from src.modules.agent.service.ai import AIService
from src.modules.agent.service.calendar import CalendarService
from src.modules.agent.dto import ContentDTO, SummaryDTO, ActionDTO


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
        return self.content_service.fetch_content(url=url, text=text)
    
    def summarize(self, content: ContentDTO) -> SummaryDTO:
        """
        Summarize content into key points.
        
        Args:
            content: ContentDTO to summarize
            
        Returns:
            SummaryDTO with summary points
        """
        summary_text = self.ai_service.summarize_text(content.text)
        return SummaryDTO(
            points=summary_text,
            source_type=content.source_type,
            character_count=len(content.text)
        )
    
    def extract_actions(self, summary: SummaryDTO) -> list[str]:
        """
        Extract actionable tasks from summary.
        
        Args:
            summary: SummaryDTO to extract actions from
            
        Returns:
            List of actionable tasks
        """
        return self.ai_service.extract_actions(summary.points)
    
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
        return self.calendar_service.add_event(action, start_time, duration_hours)
