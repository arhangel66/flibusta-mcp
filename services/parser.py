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

    def parse_author_books(self, html: str, author_name: str = None) -> list[Book]:
        """Parse books from author page."""
        soup = BeautifulSoup(html, "lxml")

        # Extract author name from page title if not provided
        if not author_name:
            title_element = soup.find("h1", class_="title")
            if title_element:
                author_name = title_element.get_text(strip=True)

        # Check if this is a date-sorted page (has h4 tags with dates)
        date_headers = soup.find_all("h4")
        if date_headers and self._is_date_format(date_headers[0].get_text(strip=True)):
            return self._parse_author_books_with_dates(soup, author_name)
        else:
            return self._parse_author_books_with_series(soup, author_name)

    def _is_date_format(self, text: str) -> bool:
        """Check if text is in date format DD.MM.YYYY."""
        return bool(re.match(r"\d{2}\.\d{2}\.\d{4}", text))

    def _parse_author_books_with_dates(
        self, soup: BeautifulSoup, author_name: str = None
    ) -> list[Book]:
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
                        book = self._parse_book_from_element(
                            element, book_link, author_name
                        )
                        if book:
                            book.added_date = current_date
                            books.append(book)
                            seen_book_ids.add(book_id)

        return books

    def _parse_author_books_with_series(
        self, soup: BeautifulSoup, author_name: str = None
    ) -> list[Book]:
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
                book = self._parse_book_from_element(link.parent, link, author_name)
                if book:
                    books.append(book)
                    seen_book_ids.add(book_id)

        return books

    def _parse_book_from_element(
        self, parent_element, book_link, author_name: str = None
    ) -> Book | None:
        """Parse a single book from its container element."""
        href = book_link.get("href", "")
        book_id = href.split("/b/")[-1] if "/b/" in href else ""

        if not book_id:
            return None

        # Extract title
        title = book_link.get_text(strip=True)
        if not title:
            return None

        # Extract authors - if we're on author page, the main author is known
        authors = []
        if author_name:
            # We're on author page, so this is the main author
            authors = [author_name]
        else:
            # Generic parsing - look for author links but exclude translators
            if parent_element:
                parent_text = parent_element.get_text()

                # If there's translator info, skip them and look for actual authors
                if "(пер." in parent_text:
                    # For translated books, the main author is usually not explicitly mentioned
                    # in the book line, so we can't determine it from this context
                    authors = ["Unknown Author"]
                else:
                    # Look for author links (not translators)
                    author_links = parent_element.find_all(
                        "a", href=re.compile(r"/a/\d+")
                    )
                    for author_link in author_links:
                        author_name_text = author_link.get_text(strip=True)
                        if author_name_text not in authors:
                            authors.append(author_name_text)

                    if not authors:
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

        # Extract book ID from script tag
        book_id = "unknown"
        script_text = soup.find("script", string=re.compile(r"var bookId"))
        if script_text:
            match = re.search(r"var bookId = (\d+)", script_text.string)
            if match:
                book_id = match.group(1)

        # Extract title from h1, remove (fb2) suffix
        title_element = soup.find("h1", class_="title")
        title = title_element.text.strip() if title_element else ""
        title = re.sub(r"\s*\(fb2\)\s*$", "", title)  # Remove (fb2) suffix

        # Extract authors - only the first author link, before (перевод:...)
        authors = []
        # Find the line with author info (usually after h1 title)
        content_area = soup.find("div", id="main")
        if content_area:
            # Look for author links that are NOT inside translation parentheses
            author_line = content_area.get_text()

            # Find the first author link before "(перевод:"
            first_author_link = content_area.find("a", href=re.compile(r"/a/\d+"))
            if first_author_link:
                # Check if this link comes before translation info
                link_text = first_author_link.get_text(strip=True)
                full_text = content_area.get_text()
                link_pos = full_text.find(link_text)
                translation_pos = full_text.find("(перевод:")

                if translation_pos == -1 or link_pos < translation_pos:
                    authors.append(link_text)

        if not authors:
            authors = ["Unknown Author"]

        # Extract year from text
        year = None
        year_match = re.search(r"издание (\d{4}) г\.", soup.text)
        if year_match:
            year = int(year_match.group(1))

        # Extract description - look for text after <h2>Аннотация</h2>
        description = ""
        annotation_header = soup.find("h2", string="Аннотация")
        if annotation_header:
            # Get the next sibling paragraph(s)
            current = annotation_header.next_sibling
            desc_parts = []
            while current:
                if current.name == "p":
                    desc_parts.append(current.get_text(strip=True))
                elif (
                    current.name == "br"
                    and current.next_sibling
                    and current.next_sibling.name != "h2"
                ):
                    # Continue to next element
                    pass
                elif current.name in ["h2", "hr", "form", "table"] or (
                    hasattr(current, "get") and current.get("id")
                ):
                    # Stop at next major element
                    break
                elif isinstance(current, str) and current.strip():
                    desc_parts.append(current.strip())
                current = current.next_sibling

            description = " ".join(desc_parts).strip()

        return Book(
            id=book_id,
            title=title,
            authors=authors,
            year=year,
            description=description,
        )

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
