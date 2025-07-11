from pathlib import Path

import pytest

from services.parser import FlibustaParser


@pytest.fixture
def parser():
    return FlibustaParser()


@pytest.fixture
def search_html():
    test_data_path = Path(__file__).parent.parent / "test_data"
    with open(test_data_path / "search_stiven_king.html", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def book_html():
    test_data_path = Path(__file__).parent.parent / "test_data"
    with open(test_data_path / "book_727250.html", "r", encoding="utf-8") as f:
        return f.read()


def test_parse_authors_from_search(parser, search_html):
    """Test parsing authors from search results page."""
    authors = parser.parse_authors_search(search_html)

    assert len(authors) == 2

    first_author = authors[0]
    assert first_author.id == "5803"
    assert first_author.name == "King Stephen"
    assert first_author.books_count == 630

    second_author = authors[1]
    assert second_author.id == "200933"
    assert second_author.name == "Stivenas Kingas"
    assert second_author.books_count == 15


def test_parse_books_from_search(parser, search_html):
    """Test parsing books from search results page."""
    books = parser.parse_books_search(search_html)

    assert len(books) == 2

    first_book = books[0]
    assert first_book.id == "727250"
    assert first_book.title == "It"
    assert first_book.authors == ["King Stephen"]
    assert first_book.year is None  # Year not parsed in search results

    second_book = books[1]
    assert second_book.id == "732128"
    assert second_book.title == "The Shining"
    assert second_book.authors == ["King Stephen"]
    assert second_book.year is None  # Year not parsed in search results


def test_parse_book_details(parser, book_html):
    """Test parsing detailed book information."""
    book = parser.parse_book_details(book_html)

    assert book.id == "727250"
    expected_title = (
        "Семь навыков на каждый день. Вечные истины в эпоху стремительных перемен"
    )
    assert book.title == expected_title
    assert book.authors == ["Шон Кови"]
    assert book.year == 2023
    assert "внутренняя потребность" in book.description


@pytest.fixture
def author_page_html():
    test_data_path = Path(__file__).parent.parent / "test_data"
    with open(test_data_path / "author_5803_default.html", "r", encoding="utf-8") as f:
        return f.read()


def test_parse_author_books_with_correct_author(parser, author_page_html):
    """Test parsing author books page with correct author identification."""
    # Parse with author name provided
    books = parser.parse_author_books(author_page_html, "Стивен Кинг")

    # Should have books
    assert len(books) > 0

    # Check that authors are correctly identified (not translators)
    for book in books[:5]:  # Check first 5 books
        assert book.authors == ["Стивен Кинг"], (
            f"Book {book.title} has wrong authors: {book.authors}"
        )
        assert book.id is not None
        assert book.title is not None


def test_parse_author_books_extracts_author_name(parser, author_page_html):
    """Test that parser can extract author name from page."""
    # Parse without author name provided - should extract from HTML
    books = parser.parse_author_books(author_page_html)

    # Should have books
    assert len(books) > 0

    # Check that author name was extracted correctly
    for book in books[:5]:  # Check first 5 books
        assert book.authors == ["Стивен Кинг"], (
            f"Book {book.title} has wrong authors: {book.authors}"
        )
