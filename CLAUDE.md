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

### 1. search_books(book_query: str) -> str
Поиск книг по запросу.
```python
await search_books("Кови")
# Возвращает JSON с найденными книгами
```

### 2. search_authors(author_query: str) -> str  
Поиск авторов по запросу.
```python
await search_authors("Кови")
# Возвращает JSON с найденными авторами
```

### 3. search_books_by_author(author_id: str) -> str
Получение всех книг автора по его ID.
```python
await search_books_by_author("50647")
# Возвращает JSON с книгами Стивена Кови
```

### 4. get_book_details(book_id: str) -> str
Получение детальной информации о книге.
```python
await get_book_details("417291")
# Возвращает JSON с деталями книги
```

### 5. download_book(book_id: str) -> str
Скачивание книги в формате EPUB.
```python
await download_book("417291")
# Скачивает книгу и возвращает путь к файлу
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
- **aiohttp** - асинхронный HTTP клиент
- **BeautifulSoup4** - парсинг HTML
- **pytest** - тестирование
- **ruff** - линтер и форматтер
- **uv** - управление зависимостями

## Установка и запуск

1. Установка зависимостей:
```bash
uv add fastmcp aiohttp beautifulsoup4 lxml
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
    book_id = books[0]["id"]
    details = await get_book_details(book_id)
    
    # Скачивание
    file_path = await download_book(book_id)
```

## Разработка

### Структура кода
- **Модели** (`models/`) - dataclass объекты для Book и Author
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

### v2.0 - Поддержка серий и сортировки по дате

✅ **Новые возможности:**
- **Поддержка серий книг** - автоматическое определение и парсинг серий
- **Сортировка по дате добавления** - параметр `order="date"` 
- **Новые MCP функции** - `get_author_series()` и `get_series_books()`
- **Исправление дублирования** - уникальные книги без повторов
- **Расширенная модель Book** - поля `series_name`, `series_id`, `added_date`

### Примеры новой функциональности

```python
# Получение книг автора с сортировкой по дате добавления
# Теперь sort_by="date" автоматически включает показ дат добавления!
books = await search_books_by_author("5803", sort_by="date", books_limit=10)

# Получение серий автора  
series = await get_author_series("5803")

# Получение книг конкретной серии
series_books = await get_series_books("18510")
```

### Исправленные проблемы

- ✅ **Дублирование книг** - убраны повторы из-за download-ссылок
- ✅ **Автоматические даты** - `sort_by="date"` теперь показывает даты добавления
- ✅ **Уникальность результатов** - каждая книга показывается только один раз

Проект готов к использованию!