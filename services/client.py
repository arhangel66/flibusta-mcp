from urllib.parse import quote_plus, urljoin

import aiofiles
import aiohttp

from config import config


class FlibustaClient:
    """HTTP client for Flibusta website."""
    
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or config.BASE_URL
        self.session: aiohttp.ClientSession | None = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=config.REQUEST_TIMEOUT),
            headers={"User-Agent": config.USER_AGENT}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_page(self, url: str) -> str:
        """Get HTML page content."""
        if not self.session:
            raise ValueError("Client session not initialized")
        
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    
    async def search_books_page(self, query: str) -> str:
        """Get search results page for books and authors."""
        encoded_query = quote_plus(query)
        url = urljoin(self.base_url, f"/booksearch?ask={encoded_query}")
        return await self.get_page(url)
    
    async def get_author_books_page(self, author_id: str) -> str:
        """Get page with all books by specific author."""
        url = urljoin(self.base_url, f"/a/{author_id}")
        return await self.get_page(url)
    
    async def get_book_details_page(self, book_id: str) -> str:
        """Get detailed book information page."""
        url = urljoin(self.base_url, f"/b/{book_id}")
        return await self.get_page(url)
    
    async def download_file(self, url: str, suggested_filename: str) -> str:
        """Download file and save to filesystem."""
        if not self.session:
            raise ValueError("Client session not initialized")
        
        downloads_dir = config.DOWNLOAD_DIR
        downloads_dir.mkdir(parents=True, exist_ok=True)
        
        async with self.session.get(url) as response:
            response.raise_for_status()
            
            # Try to get filename from Content-Disposition header
            filename = suggested_filename
            if 'content-disposition' in response.headers:
                content_disp = response.headers['content-disposition']
                if 'filename=' in content_disp:
                    # Extract filename from header like: attachment; filename="book.epub"
                    import re
                    match = re.search(r'filename[*]?=[\'"]?([^\'";]+)', content_disp)
                    if match:
                        filename = match.group(1)
            
            file_path = downloads_dir / filename
            
            async with aiofiles.open(file_path, "wb") as f:
                async for chunk in response.content.iter_chunked(8192):
                    await f.write(chunk)
        
        return str(file_path)
    
    async def try_download_book(self, book_id: str, suggested_filename: str = None) -> str:
        """Try to download book using different URL patterns."""
        download_urls = [
            urljoin(self.base_url, f"/b/{book_id}/epub"),
            urljoin(self.base_url, f"/b/{book_id}/download")
        ]
        
        filename = suggested_filename or f"book_{book_id}.epub"
        
        for url in download_urls:
            try:
                return await self.download_file(url, filename)
            except aiohttp.ClientError:
                continue
        
        raise Exception(f"Failed to download book {book_id} from all URLs")
