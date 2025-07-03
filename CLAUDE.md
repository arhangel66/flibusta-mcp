# Flibusta MCP Server

MCP (Model Context Protocol) сервер для поиска и скачивания книг с сайта Flibusta.

## Описание

Этот проект реализует MCP сервер, который предоставляет возможность:
- Поиска книг по названию/содержанию
- Поиска авторов
- Получения списка книг по автору
- Получения детальной информации о книге
- Скачивания книг в формате EPUB

## Архитектура

Проект построен по принципам OOP с dependency injection:

```
📁 mcp_books/
├── 🐍 flibusta_mcp.py      # Основной MCP сервер
├── 🔧 construct.py         # Dependency Injection
├── ⚙️  config.py           # Настройки
├── 📚 models/              # Модели данных (Book, Author)
├── 🛠  services/           # Бизнес-логика
│   ├── client.py          # HTTP клиент (aiohttp)
│   ├── parser.py          # HTML парсер (BeautifulSoup)
│   └── service.py         # Основной сервис
├── 🧪 tests/              # Юнит тесты
└── 📄 test_data/          # HTML примеры для тестов
```

## Функции MCP

### 1. search_books(book_query: str) -> List[Book]
Поиск книг по запросу.
```python
books = await search_books("Кови")
# Возвращает список объектов Book
```

### 2. search_authors(author_query: str) -> List[Author]
Поиск авторов по запросу.
```python
authors = await search_authors("Кови")
# Возвращает список объектов Author
```

### 3. search_books_by_author(author_id: str, books_limit: int = 50, sort_by: str = "default") -> List[Book]
Получение всех книг автора по его ID.
```python
books = await search_books_by_author("50647", books_limit=10, sort_by="date")
# Возвращает список объектов Book
```

### 4. get_book_details(book_id: str) -> Book
Получение детальной информации о книге.
```python
book = await get_book_details("417291")
# Возвращает объект Book с полными данными
```

### 5. download_book(book_id: str) -> Dict[str, str]
Скачивание книги в формате EPUB.
```python
result = await download_book("417291")
# Возвращает: {"status": "success", "file_path": "/path/to/file.epub", "book_id": "417291"}
```

### 6. get_author_series(author_id: str) -> List[Dict[str, str]]
Получение серий книг автора.
```python
series = await get_author_series("5803")
# Возвращает список серий: [{"id": "18510", "name": "Серия книг"}]
```

### 7. get_series_books(series_id: str) -> List[Book]
Получение книг из серии.
```python
books = await get_series_books("18510")
# Возвращает список объектов Book из серии
```

## Конфигурация

### Переменные окружения
- `FLIBUSTA_DOWNLOAD_DIR` - папка для скачивания книг (по умолчанию: `~/Documents/books/`)

### Настройка MCP
В `mcp_config.json` или клиенте MCP:
```json
{
  "mcpServers": {
    "flibusta": {
      "command": "python",
      "args": ["/path/to/flibusta_mcp.py"]
    }
  }
}
```

## Технологии

- **FastMCP** - MCP фреймворк
- **Pydantic** - валидация данных и типизация
- **aiohttp** - асинхронный HTTP клиент
- **BeautifulSoup4** - парсинг HTML
- **pytest** - тестирование
- **ruff** - линтер и форматтер
- **uv** - управление зависимостями

## Установка и запуск

1. Установка зависимостей:
```bash
uv add fastmcp aiohttp beautifulsoup4 lxml pydantic
```

2. Запуск MCP сервера:
```bash
python flibusta_mcp.py
```

3. Запуск тестов:
```bash
pytest tests/
```

## Примеры использования

### Поиск книги Стивена Кови
```python
# 1. Поиск автора
authors = await search_authors("Кови")
stephen_covey_id = "50647"  # ID Стивена Кови

# 2. Получение книг автора
books = await search_books_by_author(stephen_covey_id)

# 3. Получение деталей книги
book_details = await get_book_details("417291")

# 4. Скачивание книги
file_path = await download_book("417291")
```

### Поиск конкретной книги
```python
# Поиск по названию
books = await search_books("7 навыков")

# Получение деталей первой найденной книги
if books:
    book_id = books[0].id
    details = await get_book_details(book_id)
    
    # Скачивание
    result = await download_book(book_id)
    if result["status"] == "success":
        print(f"Скачано: {result['file_path']}")
```

## Разработка

### Структура кода
- **Модели** (`models/`) - Pydantic модели для Book и Author
- **Сервисы** (`services/`) - бизнес-логика разделена на клиент, парсер и основной сервис
- **Тесты** (`tests/`) - юнит тесты с моками и реальными HTML примерами
- **Конфигурация** (`config.py`) - централизованная конфигурация

### Принципы
- **Fail Fast** - быстрое обнаружение ошибок
- **Type Hints** - полная типизация в стиле Python 3.12
- **Async/Await** - асинхронное программирование
- **Dependency Injection** - создание объектов в `construct.py`
- **TDD** - разработка через тесты

### Качество кода
```bash
# Проверка стиля
ruff check .

# Автоисправление
ruff check --fix .

# Запуск тестов
pytest tests/
```

## Статус проекта

✅ **Полностью рабочий MCP сервер**

Все основные функции реализованы и протестированы:
- Поиск книг и авторов
- Получение деталей книг
- Скачивание в EPUB формате
- Настраиваемая папка загрузок
- Асинхронная обработка
- Обработка ошибок
- Юнит тесты

## Последние обновления

### v3.0 - Структурированные данные (Pydantic)

✅ **Новые возможности:**
- **Pydantic модели** - замена dataclass на Pydantic для лучшей валидации
- **Структурированные возвращаемые данные** - вместо строк возвращаются типизированные объекты
- **Улучшенная типизация** - полная типизация всех возвращаемых значений
- **Лучшая интеграция с MCP** - следование лучшим практикам 2024 года
- **JSON Schema** - автоматическая генерация схем для валидации

### v2.0 - Поддержка серий и сортировки по дате

✅ **Предыдущие возможности:**
- **Поддержка серий книг** - автоматическое определение и парсинг серий
- **Сортировка по дате добавления** - параметр `sort_by="date"` 
- **Новые MCP функции** - `get_author_series()` и `get_series_books()`
- **Исправление дублирования** - уникальные книги без повторов
- **Расширенная модель Book** - поля `series_name`, `series_id`, `added_date`

### Примеры новой функциональности

```python
# Получение книг автора с сортировкой по дате добавления
books = await search_books_by_author("5803", sort_by="date", books_limit=10)
# Возвращает List[Book] - список объектов Book

# Получение серий автора  
series = await get_author_series("5803")
# Возвращает List[Dict[str, str]] - список серий

# Получение книг конкретной серии
series_books = await get_series_books("18510")
# Возвращает List[Book] - список объектов Book

# Работа с объектами Book
for book in books:
    print(f"Название: {book.title}")
    print(f"Авторы: {', '.join(book.authors)}")
    print(f"Год: {book.year}")
    if book.series_name:
        print(f"Серия: {book.series_name}")
    if book.download_links:
        print(f"Скачать: {book.download_links}")
```

### Исправленные проблемы

- ✅ **Структурированные данные** - замена текстовых ответов на типизированные объекты
- ✅ **Pydantic валидация** - автоматическая проверка и валидация данных
- ✅ **Лучшая типизация** - полная типизация всех возвращаемых значений
- ✅ **JSON Schema** - автоматическая генерация схем для MCP клиентов
- ✅ **Соответствие стандартам** - следование лучшим практикам MCP 2024

Проект готов к использованию!