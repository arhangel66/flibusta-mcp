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
        sort_by: str = "default",
    ) -> list[Book]:
        """Get books by specific author."""
        order = "date" if sort_by == "date" else "default"
        html = await self.client.get_author_books_page(author_id, order=order)
        books = self.parser.parse_author_books(html)

        # Apply sorting
        if sort_by == "date":
            if order == "date" and any(book.added_date for book in books):
                # Sort by added_date if available - convert to comparable format
                def date_key(book):
                    if not book.added_date:
                        return "9999.99.99"
                    # Convert DD.MM.YYYY to YYYY.MM.DD for proper sorting
                    parts = book.added_date.split(".")
                    if len(parts) == 3:
                        return f"{parts[2]}.{parts[1]}.{parts[0]}"
                    return book.added_date

                books.sort(key=date_key, reverse=True)
            elif all(book.year for book in books):
                # Fallback to publication year
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
        safe_title = re.sub(r'[<>:"/\\|?*]', "_", title)
        # Limit length to reasonable size
        if len(safe_title) > 100:
            safe_title = safe_title[:97] + "..."
        return safe_title

    async def get_author_series(self, author_id: str) -> list[dict]:
        """Get all series for specific author."""
        html = await self.client.get_author_books_page(author_id)
        return self.parser.parse_author_series(html)

    async def get_series_books(self, series_id: str) -> list[Book]:
        """Get books from specific series."""
        html = await self.client.get_series_page(series_id)
        return self.parser.parse_author_books(html)
