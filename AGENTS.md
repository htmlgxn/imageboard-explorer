# AGENTS.md - Coding Guidelines for imageboard-explorer

This document provides guidelines for AI coding agents working on this repository.

## Build / Test / Run Commands

```bash
# Run the application (default: 127.0.0.1:8000)
uv run imageboard-explorer

# Run with auto-reload (development)
uv run uvicorn imageboard_explorer.main:app --reload

# Run all tests
uv run --dev pytest tests/ -v

# Run a single test
uv run --dev pytest tests/test_text.py::test_html_to_text_strips_tags_and_br -v

# Run tests matching a pattern
uv run --dev pytest tests/ -k "test_cache" -v

# Install dev dependencies
uv sync --dev
```

## Code Style & Formatting

**Python Version:** 3.14.3+

**Formatter & Linter:** Ruff (line length: 88)
**Type Checker:** mypy (strict mode enabled)

```bash
# Format and lint code
uv run ruff format src/ tests/
uv run ruff check --fix src/ tests/

# Type check
uv run mypy src/ tests/
```

## Import Conventions

Group imports in this order (Ruff handles this automatically):
1. Standard library (with `from __future__` first if needed)
2. Third-party packages
3. Local imports (from `.module`)

Example:
```python
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request
from httpx import HTTPStatusError

from .clients.chan_api import ChanAPIClient
from .models import Board, country_flag_url
```

## Type Hints

**REQUIRED:** All function definitions must have type hints (enforced by mypy).

```python
# Good
def helper(data: dict[str, int]) -> list[str]:
    return list(data.keys())

# Good - returns None
def process() -> None:
    pass

# Bad - missing return type
def helper(data: dict[str, int]):
    pass
```

Use `Optional[T]` for nullable types, not `T | None` (Python 3.13+ can use either, be consistent).

## Naming Conventions

- **Functions/variables:** `snake_case` (e.g., `fetch_json`, `board_list`)
- **Classes:** `PascalCase` (e.g., `ChanAPIClient`, `Board`)
- **Constants:** `UPPER_CASE` (e.g., `IMAGE_EXTS`)
- **Private methods/vars:** `_leading_underscore` (e.g., `_load_thread_posts`)
- **Path parameters:** Import as `PathParam` to avoid shadowing `pathlib.Path`

## Error Handling

**Use specific exceptions, never bare `except Exception:`**

```python
# Good
from httpx import HTTPStatusError, TimeoutException

try:
    data = await client.fetch_json(url, ttl=60)
except HTTPStatusError as e:
    logger.error(f"HTTP {e.response.status_code}")
except TimeoutException:
    logger.error("Request timed out")

# Bad
try:
    data = await client.fetch_json(url, ttl=60)
except Exception:  # Too broad!
    pass
```

## Testing Guidelines

- Write tests in `tests/test_*.py` files
- Use simple functions (no classes required)
- Import from `imageboard_explorer.module`, not `app.module`
- Test function names: `test_descriptive_name()`
- Use assertions, no need for complex fixtures for simple tests

Example:
```python
from imageboard_explorer.text import html_to_text

def test_html_to_text_strips_br():
    raw = "Hello<br>World"
    assert html_to_text(raw) == "Hello\nWorld"
```

## Project Structure

```
src/imageboard_explorer/
├── __init__.py
├── main.py           # FastAPI app, routes (keep lean)
├── models.py         # Pydantic models, helper functions
├── text.py           # Text processing utilities
├── clients/
│   ├── __init__.py
│   └── chan_api.py   # API client with caching
├── static/           # CSS, JS, images
└── templates/        # Jinja2 HTML templates
tests/
├── test_cache.py
├── test_media.py
├── test_text.py
└── test_urls.py
```

## Key Implementation Notes

1. **Package paths:** Use `Path(__file__).parent` for package-relative paths
2. **Cache:** `TTLCache` has LRU eviction with 100 entry default
3. **Validation:** Board codes validated with pattern `^[a-z]{1,6}$`
4. **Security:** Validate URLs in `text.py` - only allow http/https schemes
5. **Templates:** Stored in package directory for distribution

## Dependency Management

```bash
# Add production dependency
uv add package_name

# Add dev dependency  
uv add --extra dev package_name

# Update lock file
uv lock
```

## Before Submitting Changes

1. Run tests: `uv run --extra dev pytest tests/ -v`
2. Ensure type hints are complete (check mypy if configured)
3. Follow import ordering (stdlib → third-party → local)
4. Keep functions focused and under 50 lines when possible
5. Add tests for new functionality
6. Update this doc if you add new tooling or conventions
