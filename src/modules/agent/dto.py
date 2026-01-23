"""Data Transfer Objects for agent module."""
import datetime
from typing import Optional
from pydantic import BaseModel


class ActionDTO(BaseModel):
    """Action data transfer object."""
    text: str
    scheduled_time: Optional[datetime.datetime] = None


class SummaryDTO(BaseModel):
    """Summary data transfer object."""
    points: str  # Markdown formatted summary
    source_type: str
    character_count: int


class ContentDTO(BaseModel):
    """Content data transfer object."""
    text: str
    source_type: str
    source_url: Optional[str] = None


class ScheduledEventDTO(BaseModel):
    """Scheduled event data transfer object."""
    action: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    event_link: Optional[str] = None
