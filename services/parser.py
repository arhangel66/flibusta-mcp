import re

from bs4 import BeautifulSoup

from models import Author, Book


class FlibustaParser:
    """Parser for Flibusta HTML pages."""

    def parse_authors_search(self, html: str) -> list[Author]:
        """Parse authors from search results page."""
        soup = BeautifulSoup(html, "lxml")
        authors = []

        # Find "Найденные писатели" section
        h3_elements = soup.find_all("h3")
        authors_section = None

        for h3 in h3_elements:
            if "писатели" in h3.text.lower():
                authors_section = h3.find_next_sibling("ul")
                break

        if not authors_section:
            return authors

        # Parse each author
        for li in authors_section.find_all("li"):
            link = li.find("a", href=re.compile(r"/a/\d+"))
            if not link:
                continue

            # Extract author ID from href="/a/5803"
            href = link.get("href", "")
            author_id = href.split("/a/")[-1] if "/a/" in href else ""

            # Extract name (clean up highlighting)
            name = link.get_text(strip=True)

            # Extract books count from text like "(26 книг)"
            books_count = 0
            li_text = li.get_text()
            match = re.search(r"\((\d+)\s+книг", li_text)
            if match:
                books_count = int(match.group(1))

            authors.append(Author(id=author_id, name=name, books_count=books_count))

        return authors

    def parse_books_search(self, html: str) -> list[Book]:
        """Parse books from search results page."""
        soup = BeautifulSoup(html, "lxml")
        books = []

        # Find "Найденные книги" section
        h3_elements = soup.find_all("h3")
        books_section = None

        for h3 in h3_elements:
            if "книги" in h3.text.lower():
                books_section = h3.find_next_sibling("ul")
                break

        if not books_section:
            return books

        # Parse each book
        for li in books_section.find_all("li"):
            book_link = li.find("a", href=re.compile(r"/b/\d+"))
            if not book_link:
                continue

            # Extract book ID from href="/b/727250"
            href = book_link.get("href", "")
            book_id = href.split("/b/")[-1] if "/b/" in href else ""

            # Extract title (clean up highlighting)
            title = book_link.get_text(strip=True)

            # Extract authors - they come after " - " separator
            authors = []
            author_links = li.find_all("a", href=re.compile(r"/a/\d+"))
            for author_link in author_links:
                authors.append(author_link.get_text(strip=True))

            # Year is not typically in search results, only in detailed pages
            year = None

            books.append(Book(id=book_id, title=title, authors=authors, year=year))

        return books

    def parse_author_books(self, html: str) -> list[Book]:
        """Parse books from author page."""
        soup = BeautifulSoup(html, "lxml")

        # Check if this is a date-sorted page (has h4 tags with dates)
        date_headers = soup.find_all("h4")
        if date_headers and self._is_date_format(date_headers[0].get_text(strip=True)):
            return self._parse_author_books_with_dates(soup)
        else:
            return self._parse_author_books_with_series(soup)

    def _is_date_format(self, text: str) -> bool:
        """Check if text is in date format DD.MM.YYYY."""
        return bool(re.match(r"\d{2}\.\d{2}\.\d{4}", text))

    def _parse_author_books_with_dates(self, soup: BeautifulSoup) -> list[Book]:
        """Parse books from author page with date sorting."""
        books = []
        current_date = None
        seen_book_ids = set()

        # Find all elements that can contain dates or book info
        elements = soup.find_all(["h4", "div"])

        for element in elements:
            if element.name == "h4":
                # This is a date header
                date_text = element.get_text(strip=True)
                if self._is_date_format(date_text):
                    current_date = date_text
            elif element.name == "div" and current_date:
                # This might contain book info - find MAIN book links
                book_links = element.find_all("a", href=re.compile(r"^/b/\d+$"))

                for book_link in book_links:
                    # Skip download links based on text content
                    link_text = book_link.get_text(strip=True)
                    if link_text in [
                        "(читать)",
                        "(fb2)",
                        "(epub)",
                        "(mobi)",
                        "(скачать epub)",
                        "(скачать pdf)",
                    ]:
                        continue

                    # Parse only if we haven't seen this book ID before
                    href = book_link.get("href", "")
                    book_id = href.split("/b/")[-1] if "/b/" in href else ""

                    if book_id and book_id not in seen_book_ids:
                        book = self._parse_book_from_element(element, book_link)
                        if book:
                            book.added_date = current_date
                            books.append(book)
                            seen_book_ids.add(book_id)

        return books

    def _parse_author_books_with_series(self, soup: BeautifulSoup) -> list[Book]:
        """Parse books from author page with series grouping."""
        books = []
        seen_book_ids = set()

        # Find all book links in author page
        book_links = soup.find_all("a", href=re.compile(r"^/b/\d+$"))

        for link in book_links:
            # Skip download links
            if link.get_text(strip=True) in [
                "(читать)",
                "(fb2)",
                "(epub)",
                "(mobi)",
                "(скачать epub)",
                "(скачать pdf)",
            ]:
                continue

            # Check for duplicates
            href = link.get("href", "")
            book_id = href.split("/b/")[-1] if "/b/" in href else ""

            if book_id and book_id not in seen_book_ids:
                book = self._parse_book_from_element(link.parent, link)
                if book:
                    books.append(book)
                    seen_book_ids.add(book_id)

        return books

    def _parse_book_from_element(self, parent_element, book_link) -> Book | None:
        """Parse a single book from its container element."""
        href = book_link.get("href", "")
        book_id = href.split("/b/")[-1] if "/b/" in href else ""

        if not book_id:
            return None

        # Extract title
        title = book_link.get_text(strip=True)
        if not title:
            return None

        # Extract authors (translators)
        authors = []
        if parent_element:
            parent_text = parent_element.get_text()

            # Check if there's translator info
            if "(пер." in parent_text:
                # Find translator links
                author_links = parent_element.find_all("a", href=re.compile(r"/a/\d+"))
                for author_link in author_links:
                    author_name = author_link.get_text(strip=True)
                    if author_name not in authors:
                        authors.append(author_name)
            else:
                # If no specific translator, assume it's the main author
                authors = ["Unknown Author"]

        # Extract series information
        series_name = None
        series_id = None

        if parent_element:
            # Look for series links like <a href="/s/18510"><span>Name</span></a>
            series_links = parent_element.find_all("a", href=re.compile(r"/s/\d+"))
            for series_link in series_links:
                series_span = series_link.find("span", class_="h8")
                if series_span:
                    series_name = series_span.get_text(strip=True)
                    series_href = series_link.get("href", "")
                    series_id = (
                        series_href.split("/s/")[-1] if "/s/" in series_href else None
                    )
                    break  # Take first series found

        # Extract year from title or surrounding text
        year = None
        if parent_element:
            year_match = re.search(r"\((\d{4})\)", parent_element.get_text())
            if year_match:
                year = int(year_match.group(1))

        return Book(
            id=book_id,
            title=title,
            authors=authors,
            year=year,
            series_name=series_name,
            series_id=series_id,
        )

    def parse_book_details(self, html: str) -> Book:
        """Parse detailed book information from book page."""
        soup = BeautifulSoup(html, "lxml")

        # Extract book ID from URL (assume it's passed separately)
        book_id = "727250"  # This should be extracted from URL

        # Extract title
        title_element = soup.find("h1")
        title = title_element.text.strip() if title_element else ""

        # Extract authors
        authors = []
        author_links = soup.find_all("a", href=re.compile(r"/a/\d+"))
        for link in author_links:
            authors.append(link.text.strip())

        # Extract year
        year = None
        year_match = re.search(r"Год:\s*(\d{4})", soup.text)
        if year_match:
            year = int(year_match.group(1))

        # Extract file size
        file_size = None
        size_match = re.search(r"Размер файла:\s*(\d+K)", soup.text)
        if size_match:
            file_size = size_match.group(1)

        # Extract description
        description = ""
        desc_div = soup.find("div", class_="description")
        if desc_div:
            description = desc_div.get_text(separator=" ", strip=True)

        # Extract download links
        download_links = self.extract_download_links(html)

        return Book(
            id=book_id,
            title=title,
            authors=authors,
            year=year,
            file_size=file_size,
            description=description,
            download_links=download_links,
        )

    def extract_download_links(self, html: str) -> dict[str, str]:
        """Extract download links from book page."""
        soup = BeautifulSoup(html, "lxml")
        download_links = {}

        # Find download links section
        download_section = soup.find("div", class_="download-links")
        if not download_section:
            return download_links

        # Extract all download links
        for link in download_section.find_all("a"):
            href = link.get("href", "")

            if "/epub" in href:
                download_links["epub"] = href
            elif "/download" in href:
                download_links["download"] = href

        return download_links

    def parse_author_series(self, html: str) -> list[dict]:
        """Parse series list from author page."""
        soup = BeautifulSoup(html, "lxml")
        series_list = []

        # Find all series links
        series_links = soup.find_all("a", href=re.compile(r"/s/\d+"))

        for link in series_links:
            series_span = link.find("span", class_="h8")
            if series_span:
                series_name = series_span.get_text(strip=True)
                series_href = link.get("href", "")
                series_id = (
                    series_href.split("/s/")[-1] if "/s/" in series_href else None
                )

                if series_id and series_name:
                    series_list.append({"id": series_id, "name": series_name})

        # Remove duplicates by ID
        seen_ids = set()
        unique_series = []
        for series in series_list:
            if series["id"] not in seen_ids:
                seen_ids.add(series["id"])
                unique_series.append(series)

        return unique_series
