"""Tests for DTO models."""
import datetime
import pytest
from src.modules.agent.dto import ContentDTO, SummaryDTO, ScheduledEventDTO, ActionDTO


class TestContentDTO:
    """Tests for ContentDTO."""
    
    def test_create_with_text(self):
        dto = ContentDTO(
            text="Sample text",
            source_type="direct text",
            source_url=None
        )
        assert dto.text == "Sample text"
        assert dto.source_type == "direct text"
        assert dto.source_url is None
    
    def test_create_with_url(self):
        dto = ContentDTO(
            text="Article content",
            source_type="article",
            source_url="https://example.com/article"
        )
        assert dto.source_url == "https://example.com/article"


class TestSummaryDTO:
    """Tests for SummaryDTO."""
    
    def test_create_summary(self):
        dto = SummaryDTO(
            points="• Point 1\n• Point 2",
            source_type="article",
            character_count=100
        )
        assert dto.character_count == 100
        assert "Point 1" in dto.points


class TestScheduledEventDTO:
    """Tests for ScheduledEventDTO."""
    
    def test_create_event(self):
        start_time = datetime.datetime(2024, 1, 1, 10, 0)
        end_time = datetime.datetime(2024, 1, 1, 11, 0)
        dto = ScheduledEventDTO(
            action="Test action",
            start_time=start_time,
            end_time=end_time,
            event_link="https://calendar.google.com/event"
        )
        assert dto.action == "Test action"
        assert dto.start_time == start_time
        assert dto.event_link is not None


class TestActionDTO:
    """Tests for ActionDTO."""
    
    def test_create_action(self):
        dto = ActionDTO(text="Do something")
        assert dto.text == "Do something"
        assert dto.scheduled_time is None
    
    def test_create_action_with_time(self):
        scheduled_time = datetime.datetime(2024, 1, 1, 10, 0)
        dto = ActionDTO(
            text="Do something",
            scheduled_time=scheduled_time
        )
        assert dto.scheduled_time == scheduled_time
