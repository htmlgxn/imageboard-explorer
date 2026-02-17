# imageboard-explorer

A TUI-style webapp for browsing imageboard content in a simplified view. Built with FastAPI + Jinja and the [4chan read-only API](https://github.com/4chan/4chan-API/).

## Overview

- Terminal-like UI for browsing boards, catalogs, threads, and posts.
- Keyboard-first navigation with rofi-style board search.
- Simplified rendering of posts, quotes, and media.

### Tech Stack

- **Backend:** FastAPI, httpx, Pydantic
- **Frontend:** Vanilla JavaScript, Jinja2 templates
- **API:** 4chan read-only API with If-Modified-Since caching

### Features

- Board selection with search overlay (rofi-inspired).
- Thread catalog and post lists in a fixed-height window with centered view / selection.
- WASD navigation for quotes and external URLs.
- Country flags on boards that support them.

### Screenshots

Click a thumbnail to view more screenshots

<table>
  <tr>
    <td><a href="SCREENS.md#home-board-selection"><img src="screens/1.png" width="220" alt="Home screen"></a>
    <td><a href="SCREENS.md#catalog-alt"><img src="screens/4.png" width="220" alt="Catalog alt view"></a>
    <td><a href="SCREENS.md#post-view"><img src="screens/6.png" width="220" alt="Post view"></a></td>
  </tr>
</table>

## Installation

### RELEASE VERSION COMING SOON - FINAL BUG FIX IN PROGRESS

**Requirements:**

[uv](https://docs.astral.sh/uv/) package manager

**Setup and Run:**

```bash
git clone https://github.com/htmlgxn/comfy-imageboard-explorer.git
cd comfy-imageboard-explorer
uv run imgboard-explorer
```
Open http://127.0.0.1/ in your web browser

### [Controls](CONTROLS.md)

View how navigate each page in order.

## Notes

- This project respects 4chan API rules and uses `If-Modified-Since` with in-memory caching.
- The app is not affiliated with or endorsed by 4chan.

## License

[Unlicense](LICENSE)
