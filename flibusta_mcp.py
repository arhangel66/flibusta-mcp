"""MCP server for Flibusta book search and download."""

from typing import Dict, List

from mcp.server.fastmcp import FastMCP

from construct import create_flibusta_service
from models.book import Author, Book

# Initialize FastMCP server
mcp = FastMCP("flibusta")

# Global service instance
service = create_flibusta_service()


@mcp.tool()
async def search_books(book_query: str) -> list[Book]:
    """Search for books by title or author name.

    Args:
        book_query: Search query (book title or author name)

    Returns:
        Formatted list of found books with basic information
    """
    async with service.client:
        books = await service.search_books(book_query)

    return books


@mcp.tool()
async def search_authors(author_query: str) -> list[Author]:
    """Search for authors by name.

    Args:
        author_query: Author name to search for

    Returns:
        Formatted list of found authors with book counts
    """
    async with service.client:
        authors = await service.search_authors(author_query)

    return authors


@mcp.tool()
async def search_books_by_author(
    author_id: str, books_limit: int = 50, sort_by: str = "default"
) -> list[Book]:
    """Get books by specific author.

    Args:
        author_id: Author ID from search_authors
        books_limit: Maximum number of books to return (default: 50)
        sort_by: Sort order - "date" (newest first) or "default" (by series)

    Returns:
        Formatted list of author's books with dates (when available)
    """
    async with service.client:
        books = await service.search_books_by_author(
            author_id=author_id, books_limit=books_limit, sort_by=sort_by
        )

    return books


@mcp.tool()
async def get_book_details(book_id: str) -> Book:
    """Get detailed information about a book.

    Args:
        book_id: Book ID from search results

    Returns:
        Detailed book information including description
    """
    async with service.client:
        book = await service.get_book_details(book_id)

    return book


@mcp.tool()
async def download_book(book_id: str) -> Dict[str, str]:
    """Download a book file.

    Args:
        book_id: Book ID from search results

    Returns:
        Path to the downloaded file
    """
    try:
        async with service.client:
            file_path = await service.download_book(book_id)
        return {"status": "success", "file_path": file_path, "book_id": book_id}
    except Exception as e:
        return {"status": "error", "message": str(e), "book_id": book_id}


@mcp.tool()
async def get_author_series(author_id: str) -> List[Dict[str, str]]:
    """Get all series for specific author.

    Args:
        author_id: Author ID from search_authors

    Returns:
        Formatted list of author's series
    """
    async with service.client:
        series_list = await service.get_author_series(author_id)

    return series_list


@mcp.tool()
async def get_series_books(series_id: str) -> List[Book]:
    """Get books from specific series.

    Args:
        series_id: Series ID from get_author_series

    Returns:
        Formatted list of books in the series
    """
    async with service.client:
        books = await service.get_series_books(series_id)

    return books


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
