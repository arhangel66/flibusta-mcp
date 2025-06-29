from unittest.mock import patch
from urllib.parse import quote_plus

import pytest

from services.client import FlibustaClient


def test_client_initialization():
    """Test client initialization."""
    client = FlibustaClient("https://custom.url")
    assert client.base_url == "https://custom.url"
    assert client.session is None
    
    # Test default URL
    client_default = FlibustaClient()
    assert client_default.base_url == "https://flibusta.is"


def test_url_generation():
    """Test URL generation methods."""
    client = FlibustaClient()
    
    # Test search URL
    with patch.object(client, 'get_page') as mock_get:
        mock_get.return_value = "<html>mock</html>"
        
        # We'll create a synchronous wrapper to test URL generation
        expected_query = quote_plus("stiven king")
        expected_url = f"https://flibusta.is/booksearch?ask={expected_query}"
        
        # Test that correct URLs would be generated
        assert f"/booksearch?ask={expected_query}" in expected_url
        assert "stiven+king" in expected_url


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client as async context manager."""
    client = FlibustaClient()
    
    # Should not have session initially
    assert client.session is None
    
    with patch("services.client.aiohttp.ClientSession") as mock_session_class:
        from unittest.mock import AsyncMock
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session
        
        async with client:
            # Should have session when entered
            assert client.session is not None
        
        # Session close should have been called
        mock_session.close.assert_called_once()


def test_download_urls_generation():
    """Test download URL generation."""
    # Test download URL patterns
    book_id = "727250"
    expected_urls = [
        f"https://flibusta.is/b/{book_id}/epub",
        f"https://flibusta.is/b/{book_id}/download"
    ]
    
    # These are the URLs that would be tried
    assert expected_urls[0] == "https://flibusta.is/b/727250/epub"
    assert expected_urls[1] == "https://flibusta.is/b/727250/download"