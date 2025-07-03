from pydantic import BaseModel


class Book(BaseModel):
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


class Author(BaseModel):
    id: str
    name: str
    books_count: int
