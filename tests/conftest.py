"""Pytest configuration and fixtures."""
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_genai_client():
    """Mock Gemini API client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mocked AI response"
    mock_client.models.generate_content.return_value = mock_response
    return mock_client


@pytest.fixture
def sample_content_dto():
    """Sample ContentDTO for testing."""
    from src.modules.agent.dto import ContentDTO
    return ContentDTO(
        text="Sample article content for testing purposes.",
        source_type="article",
        source_url="https://example.com/article"
    )


@pytest.fixture
def sample_summary_dto():
    """Sample SummaryDTO for testing."""
    from src.modules.agent.dto import SummaryDTO
    return SummaryDTO(
        points="• Point 1\n• Point 2\n• Point 3",
        source_type="article",
        character_count=100
    )
