from models import Author, Book

from .client import FlibustaClient
from .parser import FlibustaParser


class FlibustaService:
    """Main service for Flibusta operations."""
    
    def __init__(self, client: FlibustaClient, parser: FlibustaParser):
        self.client = client
        self.parser = parser
    
    async def search_books(self, query: str) -> list[Book]:
        """Search for books by title or author name."""
        html = await self.client.search_books_page(query)
        return self.parser.parse_books_search(html)
    
    async def search_authors(self, query: str) -> list[Author]:
        """Search for authors by name."""
        html = await self.client.search_books_page(query)
        return self.parser.parse_authors_search(html)
    
    async def search_books_by_author(
        self, 
        author_id: str, 
        books_limit: int = 50,
        sort_by: str = "date"
    ) -> list[Book]:
        """Get books by specific author."""
        html = await self.client.get_author_books_page(author_id)
        books = self.parser.parse_author_books(html)
        
        # Apply sorting
        if sort_by == "alphabet":
            books.sort(key=lambda book: book.title.lower())
        elif sort_by == "date" and all(book.year for book in books):
            books.sort(key=lambda book: book.year or 0, reverse=True)
        
        # Apply limit
        return books[:books_limit]
    
    async def get_book_details(self, book_id: str) -> Book:
        """Get detailed information about a book."""
        html = await self.client.get_book_details_page(book_id)
        book = self.parser.parse_book_details(html)
        book.id = book_id  # Ensure correct ID
        return book
    
    async def download_book(self, book_id: str) -> str:
        """Download book and return file path."""
        # Get book details to create proper filename
        try:
            book = await self.get_book_details(book_id)
            # Create safe filename from book title
            safe_title = self._create_safe_filename(book.title)
            suggested_filename = f"{safe_title}.epub"
        except Exception:
            # Fallback to generic name if can't get details
            suggested_filename = f"book_{book_id}.epub"
        
        return await self.client.try_download_book(book_id, suggested_filename)
    
    def _create_safe_filename(self, title: str) -> str:
        """Create filesystem-safe filename from book title."""
        import re
        # Remove or replace problematic characters
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        # Limit length to reasonable size
        if len(safe_title) > 100:
            safe_title = safe_title[:97] + "..."
        return safe_title