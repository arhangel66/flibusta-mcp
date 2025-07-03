from dataclasses import dataclass


@dataclass
class Book:
    id: str
    title: str
    authors: list[str]
    download_links: dict[str, str] | None = None
    year: int | None = None
    description: str | None = None
    file_size: str | None = None
    series_name: str | None = None
    series_id: str | None = None
    added_date: str | None = None


@dataclass
class Author:
    id: str
    name: str
    books_count: int
