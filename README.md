# comfy-imageboard-explorer

A TUI-style webapp for browsing imageboard content in a simplified view. Built with FastAPI + Jinja and the [4chan read-only API](https://github.com/4chan/4chan-API/).

## Overview

- Terminal-like UI for browsing boards, catalogs, threads, and posts.
- Keyboard-first navigation with rofi-style board search.
- Simplified rendering of posts, quotes, and media.

## Features

- Board selection with inline search overlay (rofi-inspired).
- Thread catalog and post lists in a fixed-height window with centered selection.
- Post view and full media view for images and webm files.
- Purple-link navigation for quotes and external URLs.
- Country flags on boards that support them.

## Controls

Home (board selection):
- `type` search
- `↑/↓` move
- `enter` select
- `esc/backspace` close search

Catalog (thread list):
- `h` home
- `↑/↓` move
- `enter` open thread
- `backspace` back

Thread (post list):
- `h` home
- `↑/↓` move
- `enter` open post / image
- `backspace` back
- `WASD` select link
- `e` open link

Post view:
- `h` home
- `backspace` back
- `WASD` select link
- `e` open link
- `enter` full image

Full image view:
- `h` home
- `backspace` back

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Notes

- This project respects 4chan API rules and uses `If-Modified-Since` with in-memory caching.
- The app is not affiliated with or endorsed by 4chan.
