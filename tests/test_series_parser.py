"""Tests for series parsing functionality."""

import pytest

from services.parser import FlibustaParser


@pytest.fixture
def parser():
    return FlibustaParser()


@pytest.fixture
def series_html():
    """Sample HTML with series data."""
    return """
    <html>
    <body>
    <h4>17.06.2025</h4>
    <div class="g-thriller g-sf_horror">
    <input type="checkbox" id="23,9-14873" name="bchk831271"> -  
    <a href="/b/831271">После заката</a> [сборник litres] 
    (пер. <a href="/a/42985">Сергей Николаевич Самуйлов</a>)  
    (<a href="/s/14873"><span class="h8">Сразу после заката</span></a>)  
    <span style="size">3079K, 350 с.</span> <a href="/b/831271/read">(читать)</a>  
    скачать: <a href="/b/831271/fb2">(fb2)</a> - <a href="/b/831271/epub">(epub)</a>
    </div>

    <h4>11.06.2025</h4>
    <div class="g-thriller g-sf_horror">
    <input type="checkbox" id="23,9-" name="bchk830578"> -  
    <a href="/b/830578">Четыре сезона</a> [сборник litres] 
    (пер. <a href="/a/174283">Виктор Вячеславович Антонов</a>)  
    <span style="size">2392K, 504 с.</span> <a href="/b/830578/read">(читать)</a>  
    скачать: <a href="/b/830578/fb2">(fb2)</a> - <a href="/b/830578/epub">(epub)</a>
    </div>

    <div>
    <a href="/s/18510"><span class="h8">Кинг, Стивен. Романы</span></a> 
    <b>&#8614;</b> <a href="/s/33189"><span class="h8">Дэнни Торранс</span></a> 
    (<a href="/g/9" class="genre" name="sf_horror">Ужасы</a>)
    <br>
    <input type="checkbox"> - <a href="/b/417291">Сияние</a> (1977) 
    <span style="size">1024K, 544 с.</span> <a href="/b/417291/read">(читать)</a>  
    скачать: <a href="/b/417291/fb2">(fb2)</a> - <a href="/b/417291/epub">(epub)</a>
    <br>
    <input type="checkbox"> - <a href="/b/512345">Доктор Сон</a> (2013) 
    <span style="size">1536K, 704 с.</span> <a href="/b/512345/read">(читать)</a>  
    скачать: <a href="/b/512345/fb2">(fb2)</a> - <a href="/b/512345/epub">(epub)</a>
    </div>
    </body>
    </html>
    """


def test_is_date_format(parser):
    """Test date format detection."""
    assert parser._is_date_format("17.06.2025") is True
    assert parser._is_date_format("11.06.2025") is True
    assert parser._is_date_format("invalid") is False
    assert parser._is_date_format("2025-06-17") is False


def test_parse_author_books_with_dates(parser, series_html):
    """Test parsing books with date sorting."""
    books = parser.parse_author_books(series_html)

    # Should find books with dates
    date_books = [book for book in books if book.added_date]
    assert len(date_books) >= 2

    # Check specific books with dates
    first_book = next((book for book in books if book.id == "831271"), None)
    assert first_book is not None
    assert first_book.added_date == "17.06.2025"
    assert first_book.title == "После заката"
    assert first_book.series_name == "Сразу после заката"
    assert first_book.series_id == "14873"

    second_book = next((book for book in books if book.id == "830578"), None)
    assert second_book is not None
    assert second_book.added_date == "11.06.2025"
    assert second_book.title == "Четыре сезона"


def test_parse_author_series(parser, series_html):
    """Test parsing series list from author page."""
    series_list = parser.parse_author_series(series_html)

    assert len(series_list) >= 3

    # Check for specific series
    series_ids = [series["id"] for series in series_list]
    series_names = [series["name"] for series in series_list]

    assert "14873" in series_ids
    assert "18510" in series_ids
    assert "33189" in series_ids

    assert "Сразу после заката" in series_names
    assert "Кинг, Стивен. Романы" in series_names
    assert "Дэнни Торранс" in series_names


def test_parse_book_from_element_with_series(parser):
    """Test parsing individual book with series info."""
    from bs4 import BeautifulSoup

    html = """
    <div>
    <input type="checkbox"> - <a href="/b/417291">Сияние</a> (1977) 
    (<a href="/s/33189"><span class="h8">Дэнни Торранс</span></a>)
    <span style="size">1024K, 544 с.</span>
    </div>
    """

    soup = BeautifulSoup(html, "lxml")
    book_link = soup.find("a", href="/b/417291")
    parent_element = book_link.parent

    book = parser._parse_book_from_element(parent_element, book_link)

    assert book is not None
    assert book.id == "417291"
    assert book.title == "Сияние"
    assert book.year == 1977
    assert book.series_name == "Дэнни Торранс"
    assert book.series_id == "33189"


def test_parse_book_without_series(parser):
    """Test parsing book without series info."""
    from bs4 import BeautifulSoup

    html = """
    <div>
    <input type="checkbox"> - <a href="/b/830578">Четыре сезона</a> [сборник litres] 
    (пер. <a href="/a/174283">Виктор Вячеславович Антонов</a>)  
    <span style="size">2392K, 504 с.</span>
    </div>
    """

    soup = BeautifulSoup(html, "lxml")
    book_link = soup.find("a", href="/b/830578")
    parent_element = book_link.parent

    # Test without author name provided (should not include translator)
    book = parser._parse_book_from_element(parent_element, book_link)
    assert book is not None
    assert book.id == "830578"
    assert book.title == "Четыре сезона"
    assert book.series_name is None
    assert book.series_id is None
    # Translators should NOT be in authors list
    assert book.authors == ["Unknown Author"]

    # Test with author name provided (should use provided author)
    book_with_author = parser._parse_book_from_element(
        parent_element, book_link, "Стивен Кинг"
    )
    assert book_with_author.authors == ["Стивен Кинг"]
