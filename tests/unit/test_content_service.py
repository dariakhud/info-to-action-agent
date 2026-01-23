"""Tests for ContentService."""
import pytest
from unittest.mock import patch, MagicMock
from src.modules.agent.service.content import ContentService
from src.modules.agent.dto import ContentDTO


class TestContentService:
    """Tests for ContentService."""
    
    def test_fetch_content_with_text(self):
        """Test fetching content from direct text."""
        result = ContentService.fetch_content(text="Sample text content")
        
        assert isinstance(result, ContentDTO)
        assert result.text == "Sample text content"
        assert result.source_type == "direct text"
        assert result.source_url is None
    
    def test_fetch_content_no_input(self):
        """Test that ValueError is raised when no input provided."""
        with pytest.raises(ValueError, match="Either url or text must be provided"):
            ContentService.fetch_content()
    
    @patch('src.modules.agent.service.content.fetch_article_text')
    @patch('src.modules.agent.service.content.is_url')
    @patch('src.modules.agent.service.content.is_youtube_url')
    def test_fetch_content_with_article_url(self, mock_is_youtube, mock_is_url, mock_fetch):
        """Test fetching content from article URL."""
        mock_is_youtube.return_value = False
        mock_is_url.return_value = True
        mock_fetch.return_value = "Article content here"
        
        result = ContentService.fetch_content(url="https://example.com/article")
        
        assert isinstance(result, ContentDTO)
        assert result.text == "Article content here"
        assert result.source_type == "article"
        assert result.source_url == "https://example.com/article"
        mock_fetch.assert_called_once_with("https://example.com/article")
    
    @patch('src.modules.agent.service.content.fetch_video_transcript')
    @patch('src.modules.agent.service.content.is_url')
    @patch('src.modules.agent.service.content.is_youtube_url')
    def test_fetch_content_with_youtube_url(self, mock_is_youtube, mock_is_url, mock_fetch):
        """Test fetching content from YouTube URL."""
        mock_is_youtube.return_value = True
        mock_is_url.return_value = True
        mock_fetch.return_value = "Video transcript content"
        
        result = ContentService.fetch_content(url="https://youtube.com/watch?v=test")
        
        assert isinstance(result, ContentDTO)
        assert result.text == "Video transcript content"
        assert result.source_type == "video transcript"
        mock_fetch.assert_called_once_with("https://youtube.com/watch?v=test")
    
    def test_fetch_content_invalid_url_format(self):
        """Test that ValueError is raised for invalid URL format."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            ContentService.fetch_content(url="not-a-url")
    
    @patch('src.modules.agent.service.content.fetch_article_text')
    @patch('src.modules.agent.service.content.is_url')
    @patch('src.modules.agent.service.content.is_youtube_url')
    def test_fetch_content_empty_result(self, mock_is_youtube, mock_is_url, mock_fetch):
        """Test that ValueError is raised when content is empty."""
        mock_is_youtube.return_value = False
        mock_is_url.return_value = True
        mock_fetch.return_value = ""
        
        with pytest.raises(ValueError, match="Could not extract text"):
            ContentService.fetch_content(url="https://example.com/article")
