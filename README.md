# Flibusta MCP Server

MCP (Model Context Protocol) server for searching and downloading books from Flibusta.

## Features

- **search_books** - Search for books by title or author name
- **search_authors** - Find authors by name  
- **search_books_by_author** - Get books by specific author with sorting and filtering
- **get_book_details** - Get detailed book information including description
- **download_book** - Download books in epub format

## Installation

```bash
# Install dependencies
uv add fastmcp aiohttp beautifulsoup4 lxml

# Run tests
pytest tests/

# Check code quality
ruff check .
```

## Usage

Start the MCP server:

```bash
python flibusta_mcp.py
```

## Architecture

Built following OOP principles with dependency injection:

- **models/** - Data models (Book, Author)
- **services/** - Business logic classes
  - `FlibustaClient` - HTTP client for Flibusta
  - `FlibustaParser` - HTML parsing logic  
  - `FlibustaService` - Main service orchestrator
- **construct.py** - Dependency injection container
- **tests/** - Unit tests with pytest

## Example Usage

```python
# Search for books
search_books("stiven king")

# Find authors
search_authors("king")

# Get author's books
search_books_by_author("5803", books_limit=10, sort_by="date")

# Get book details
get_book_details("727250")

# Download book
download_book("727250")
```

## Development

Uses TDD approach with comprehensive test coverage for parsers and business logic.