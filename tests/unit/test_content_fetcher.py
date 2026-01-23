"""Tests for content fetcher utilities."""
import pytest
from src.infra.client.content_fetcher import is_url, is_youtube_url


class TestIsUrl:
    """Tests for is_url function."""
    
    def test_valid_http_url(self):
        assert is_url("http://example.com") is True
    
    def test_valid_https_url(self):
        assert is_url("https://example.com") is True
    
    def test_url_with_path(self):
        assert is_url("https://example.com/article") is True
    
    def test_not_url_text(self):
        assert is_url("just some text") is False
    
    def test_not_url_empty(self):
        assert is_url("") is False
    
    def test_url_with_whitespace(self):
        assert is_url("  https://example.com  ") is True


class TestIsYoutubeUrl:
    """Tests for is_youtube_url function."""
    
    def test_standard_youtube_url(self):
        assert is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True
    
    def test_youtube_short_url(self):
        assert is_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True
    
    def test_youtube_embed_url(self):
        assert is_youtube_url("https://www.youtube.com/embed/dQw4w9WgXcQ") is True
    
    def test_youtube_without_www(self):
        assert is_youtube_url("https://youtube.com/watch?v=dQw4w9WgXcQ") is True
    
    def test_not_youtube_url(self):
        assert is_youtube_url("https://example.com/video") is False
    
    def test_not_url(self):
        assert is_youtube_url("just text") is False
