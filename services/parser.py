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
            
            authors.append(Author(
                id=author_id,
                name=name,
                books_count=books_count
            ))
        
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
            
            books.append(Book(
                id=book_id,
                title=title,
                authors=authors,
                year=year
            ))
        
        return books
    
    def parse_author_books(self, html: str) -> list[Book]:
        """Parse books from author page."""
        soup = BeautifulSoup(html, "lxml")
        books = []
        
        # Find all book links in author page, but filter out download links
        # Books are in links like: <a href="/b/417291">Book Title</a>
        # Exclude: /read, /fb2, /epub, /mobi, /download
        book_links = soup.find_all("a", href=re.compile(r"^/b/\d+$"))
        
        for link in book_links:
            href = link.get("href", "")
            book_id = href.split("/b/")[-1] if "/b/" in href else ""
            
            if not book_id:
                continue
            
            # Extract title
            title = link.get_text(strip=True)
            
            # Skip empty titles or obvious download links
            if not title or title in ["(читать)", "(fb2)", "(epub)", "(mobi)", "(скачать epub)", "(скачать pdf)"]:
                continue
            
            # For author page, the main author is known, 
            # but we can extract translators from surrounding text
            authors = []
            
            # Find the parent element to get context
            parent = link.parent
            if parent:
                # Look for translator info like "(пер. Author Name)"
                parent_text = parent.get_text()
                
                # Check if there's translator info
                if "(пер." in parent_text:
                    # Find translator links
                    author_links = parent.find_all("a", href=re.compile(r"/a/\d+"))
                    for author_link in author_links:
                        author_name = author_link.get_text(strip=True)
                        if author_name not in authors:
                            authors.append(author_name)
                else:
                    # If no specific translator, assume it's the main author
                    # We could extract from page title/h1, but for now use placeholder
                    authors = ["Unknown Author"]
            
            # If no authors found, skip this entry
            if not authors:
                continue
            
            books.append(Book(
                id=book_id,
                title=title,
                authors=authors,
                year=None  # Year typically not shown on author page
            ))
        
        return books
    
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
            download_links=download_links
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