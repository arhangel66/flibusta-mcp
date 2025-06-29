"""MCP server for Flibusta book search and download."""


from mcp.server.fastmcp import FastMCP

from construct import create_flibusta_service

# Initialize FastMCP server
mcp = FastMCP("flibusta")

# Global service instance
service = create_flibusta_service()


@mcp.tool()
async def search_books(book_query: str) -> str:
    """Search for books by title or author name.
    
    Args:
        book_query: Search query (book title or author name)
    
    Returns:
        Formatted list of found books with basic information
    """
    async with service.client:
        books = await service.search_books(book_query)
    
    if not books:
        return "No books found for the given query."
    
    result = f"Found {len(books)} books:\n\n"
    for book in books:
        authors_str = ", ".join(book.authors)
        year_str = f" ({book.year})" if book.year else ""
        result += f"• {book.title} by {authors_str}{year_str}\n"
        result += f"  ID: {book.id}\n\n"
    
    return result


@mcp.tool()
async def search_authors(author_query: str) -> str:
    """Search for authors by name.
    
    Args:
        author_query: Author name to search for
    
    Returns:
        Formatted list of found authors with book counts
    """
    async with service.client:
        authors = await service.search_authors(author_query)
    
    if not authors:
        return "No authors found for the given query."
    
    result = f"Found {len(authors)} authors:\n\n"
    for author in authors:
        result += f"• {author.name} - {author.books_count} books\n"
        result += f"  ID: {author.id}\n\n"
    
    return result


@mcp.tool()
async def search_books_by_author(
    author_id: str, 
    books_limit: int = 50, 
    sort_by: str = "date"
) -> str:
    """Get books by specific author.
    
    Args:
        author_id: Author ID from search_authors
        books_limit: Maximum number of books to return (default: 50)
        sort_by: Sort order - "date" (newest first) or "alphabet" (default: "date")
    
    Returns:
        Formatted list of author's books with download links
    """
    async with service.client:
        books = await service.search_books_by_author(
            author_id=author_id,
            books_limit=books_limit,
            sort_by=sort_by
        )
    
    if not books:
        return f"No books found for author ID: {author_id}"
    
    result = f"Found {len(books)} books by this author:\n\n"
    for book in books:
        year_str = f" ({book.year})" if book.year else ""
        result += f"• {book.title}{year_str}\n"
        result += f"  ID: {book.id}\n"
        
        if book.download_links:
            result += "  Download: "
            links = []
            for format_name, url in book.download_links.items():
                links.append(f"{format_name} ({url})")
            result += ", ".join(links)
            result += "\n"
        
        result += "\n"
    
    return result


@mcp.tool()
async def get_book_details(book_id: str) -> str:
    """Get detailed information about a book.
    
    Args:
        book_id: Book ID from search results
    
    Returns:
        Detailed book information including description and download links
    """
    async with service.client:
        book = await service.get_book_details(book_id)
    
    authors_str = ", ".join(book.authors)
    size_str = f" - {book.file_size}" if book.file_size else ""
    
    result = "Book Details:\n\n"
    result += f"Title: {book.title}\n"
    result += f"Authors: {authors_str}\n"
    result += f"Year: {book.year or 'Unknown'}\n"
    result += f"File Size: {book.file_size or 'Unknown'}{size_str}\n\n"
    
    if book.description:
        result += f"Description:\n{book.description}\n\n"
    
    if book.download_links:
        result += "Download Links:\n"
        for format_name, url in book.download_links.items():
            result += f"• {format_name}: {url}\n"
    
    return result


@mcp.tool()
async def download_book(book_id: str) -> str:
    """Download a book file.
    
    Args:
        book_id: Book ID from search results
    
    Returns:
        Path to the downloaded file
    """
    try:
        async with service.client:
            file_path = await service.download_book(book_id)
        return f"Book downloaded successfully: {file_path}"
    except Exception as e:
        return f"Failed to download book {book_id}: {str(e)}"


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")