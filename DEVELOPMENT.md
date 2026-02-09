# Development Guide

This guide covers how to set up the development environment and contribute to comfy-imageboard-explorer.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager

## Getting Started

### Quick Install (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/htmlgxn/comfy-imageboard-explorer/main/scripts/install.sh | bash -s -- --dev
```

This will:
1. Clone the repository to `~/projects/imgboard-explorer`
2. Install all dependencies (including dev dependencies)
3. Create a `imgboard-explorer-dev` command

The app will be available at http://127.0.0.1:8000

**Customize install location:**
```bash
# Non-interactive - specify directory via environment variable
DEV_DIR=~/code/imgboard-explorer curl -sSL https://raw.githubusercontent.com/htmlgxn/comfy-imageboard-explorer/main/scripts/install.sh | bash -s -- --dev
```

### Manual Setup

```bash
# Clone the repository
git clone https://github.com/htmlgxn/comfy-imageboard-explorer.git
cd comfy-imageboard-explorer

# Install dependencies (including dev dependencies)
uv sync --dev

# Run the application
uv run imgboard-explorer
```

The app will be available at http://127.0.0.1:8000

## Development Mode

For development with auto-reload:

```bash
uv run uvicorn imgboard_explorer.main:app --reload
```

## Uninstall

```bash
curl -sSL https://raw.githubusercontent.com/htmlgxn/comfy-imageboard-explorer/main/scripts/install.sh | bash -s -- --uninstall
```

This will uninstall both regular and dev versions if installed.

## Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run a specific test
uv run pytest tests/test_text.py::test_html_to_text_strips_tags_and_br -v

# Run tests matching a pattern
uv run pytest tests/ -k "test_cache" -v
```

## Code Quality

The project uses several tools to maintain code quality:

```bash
# Format and lint code
uv run ruff format src/ tests/
uv run ruff check --fix src/ tests/

# Type checking
uv run mypy src/ tests/
```

## Project Structure

```
src/imgboard_explorer/
├── __init__.py
├── main.py           # FastAPI app and routes
├── models.py         # Pydantic models and helpers
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

## Making Changes

1. Create a new branch for your changes
2. Write or update tests as needed
3. Run the test suite to ensure everything passes
4. Format and type-check your code
5. Submit a pull request

## Tech Stack

- **Backend:** FastAPI, httpx, Pydantic
- **Frontend:** Vanilla JavaScript, Jinja2 templates
- **Testing:** pytest
- **Package Management:** uv

## API Notes

The app uses the [4chan read-only API](https://github.com/4chan/4chan-API/) with:
- Rate limiting (1 request per second)
- In-memory caching with `If-Modified-Since` headers
- TTL-based cache expiration

## License

[Unlicense](../LICENSE)
