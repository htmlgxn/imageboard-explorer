import argparse
import html as html_lib
import subprocess
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Path as PathParam, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from httpx import HTTPStatusError

from .clients.chan_api import ChanAPIClient
from .models import (
    Board,
    CatalogThread,
    Thread,
    ThreadPost,
    country_flag_url,
    format_bytes,
    image_url,
    media_kind,
    thumbnail_url,
)
from .text import (
    extract_all_quotes,
    extract_quotes,
    html_to_text,
    strip_header_quotes,
    text_to_html,
)

_PACKAGE_DIR = Path(__file__).parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(_PACKAGE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(_PACKAGE_DIR / "templates"))
client = ChanAPIClient()


@app.on_event("startup")
async def startup() -> None:
    await client.start()


@app.on_event("shutdown")
async def shutdown() -> None:
    await client.aclose()


def _board_description(board: Board) -> str:
    description = board.meta_description or board.title
    return html_lib.unescape(description)


async def _load_boards() -> list[Board]:
    payload = await client.fetch_json("/boards.json", ttl_seconds=3600)
    return [Board(**board) for board in payload.get("boards", [])]


def _build_post_payload(
    board: str, thread_id: int, post: ThreadPost, reply_from: list[int]
) -> dict:
    comment_text = html_to_text(post.com)
    quotes_header, quotes_body = extract_quotes(comment_text)
    full_image_url = image_url(board, post.tim, post.ext)
    body_text = strip_header_quotes(comment_text)
    media_type = media_kind(post.ext)
    file_name = f"{post.filename}{post.ext}" if post.filename and post.ext else None
    file_size = format_bytes(post.fsize)
    country = post.country
    country_name = post.country_name
    return {
        "no": post.no,
        "name": post.name or "Anonymous",
        "now": post.now or "",
        "comment_html": text_to_html(body_text),
        "thumbnail_url": thumbnail_url(board, post.tim),
        "quotes_header": quotes_header,
        "quotes_body": quotes_body,
        "reply_from": reply_from,
        "image_url": full_image_url,
        "media_kind": media_type,
        "file_name": file_name,
        "file_size": file_size,
        "country": country,
        "country_name": country_name,
        "country_flag_url": country_flag_url(country),
        "image_view_href": (
            f"/board/{board}/thread/{thread_id}/post/{post.no}"
            if full_image_url
            else None
        ),
        "image_full_href": (
            f"/board/{board}/thread/{thread_id}/post/{post.no}/image"
            if full_image_url
            else None
        ),
    }


async def _load_thread_posts(board: str, thread_id: int) -> list[dict]:
    payload = await client.fetch_json(
        f"/{board}/thread/{thread_id}.json", ttl_seconds=10
    )
    thread_data = Thread(**payload)
    posts = thread_data.posts
    post_ids = {post.no for post in posts}
    reply_from_map: dict[int, list[int]] = {post.no: [] for post in posts}

    for post in posts:
        comment_text = html_to_text(post.com)
        for quoted_id in extract_all_quotes(comment_text):
            try:
                quoted_no = int(quoted_id)
            except ValueError:
                continue
            if quoted_no not in post_ids or quoted_no == post.no:
                continue
            existing = reply_from_map.get(quoted_no)
            if existing is None:
                reply_from_map[quoted_no] = [post.no]
            elif post.no not in existing:
                existing.append(post.no)

    return [
        _build_post_payload(board, thread_id, post, reply_from_map.get(post.no, []))
        for post in posts
    ]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, selected: str | None = None) -> HTMLResponse:
    try:
        boards = await _load_boards()
    except Exception:
        return templates.TemplateResponse(
            "home.html",
            {
                "request": request,
                "screen": "home",
                "error": "Unable to load boards right now. Please try again.",
            },
            status_code=502,
        )

    if not boards:
        return templates.TemplateResponse(
            "home.html",
            {
                "request": request,
                "screen": "home",
                "error": "No boards available.",
            },
            status_code=502,
        )

    selected_board = next(
        (board for board in boards if board.board == selected), boards[0]
    )
    board_items = []
    for board in boards:
        board_items.append(
            {
                "board": board.board,
                "title": board.title,
                "ws_board": board.ws_board,
                "description": _board_description(board),
            }
        )

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "screen": "home",
            "boards": board_items,
            "selected": selected_board.board,
            "selected_description": _board_description(selected_board),
        },
    )


@app.get("/board/{board}/catalog", response_class=HTMLResponse)
async def catalog(
    request: Request,
    board: str = PathParam(..., pattern=r"^[a-z]{1,6}$"),
    selected: int | None = None,
) -> HTMLResponse:
    try:
        payload = await client.fetch_json(f"/{board}/catalog.json", ttl_seconds=30)
    except HTTPStatusError as exc:
        status_code = exc.response.status_code
        message = (
            "Board not found."
            if status_code == 404
            else "Unable to load catalog right now."
        )
        return templates.TemplateResponse(
            "catalog.html",
            {"request": request, "screen": "catalog", "board": board, "error": message},
            status_code=status_code,
        )
    except Exception:
        return templates.TemplateResponse(
            "catalog.html",
            {
                "request": request,
                "screen": "catalog",
                "board": board,
                "error": "Unable to load catalog right now.",
            },
            status_code=502,
        )

    threads = []
    for page in payload:
        for item in page.get("threads", []):
            thread = CatalogThread(**item)
            comment_text = html_to_text(thread.com)
            threads.append(
                {
                    "no": thread.no,
                    "name": thread.name or "Anonymous",
                    "now": thread.now or "",
                    "sub": thread.sub,
                    "comment_html": text_to_html(comment_text),
                    "thumbnail_url": thumbnail_url(board, thread.tim),
                    "replies": thread.replies,
                    "images": thread.images,
                    "country": thread.country,
                    "country_name": thread.country_name,
                    "country_flag_url": country_flag_url(thread.country),
                }
            )

    if threads:
        selected_thread = next((t for t in threads if t["no"] == selected), threads[0])
        selected_id = selected_thread["no"]
    else:
        selected_id = None

    return templates.TemplateResponse(
        "catalog.html",
        {
            "request": request,
            "screen": "catalog",
            "board": board,
            "threads": threads,
            "selected": selected_id,
        },
    )


@app.get("/board/{board}/thread/{thread_id}", response_class=HTMLResponse)
async def thread(
    request: Request,
    board: str = PathParam(..., pattern=r"^[a-z]{1,6}$"),
    thread_id: int = PathParam(..., ge=1),
    selected: int | None = None,
) -> HTMLResponse:
    try:
        posts = await _load_thread_posts(board, thread_id)
    except HTTPStatusError as exc:
        status_code = exc.response.status_code
        message = (
            "Thread not found."
            if status_code == 404
            else "Unable to load thread right now."
        )
        return templates.TemplateResponse(
            "thread.html",
            {
                "request": request,
                "screen": "thread",
                "board": board,
                "error": message,
            },
            status_code=status_code,
        )
    except Exception:
        return templates.TemplateResponse(
            "thread.html",
            {
                "request": request,
                "screen": "thread",
                "board": board,
                "error": "Unable to load thread right now.",
            },
            status_code=502,
        )

    if posts:
        selected_post = next((p for p in posts if p["no"] == selected), posts[0])
        selected_id = selected_post["no"]
    else:
        selected_id = None

    return templates.TemplateResponse(
        "thread.html",
        {
            "request": request,
            "screen": "thread",
            "board": board,
            "posts": posts,
            "selected": selected_id,
        },
    )


@app.get(
    "/board/{board}/thread/{thread_id}/post/{post_id}", response_class=HTMLResponse
)
async def post_view(
    request: Request,
    board: str = PathParam(..., pattern=r"^[a-z]{1,6}$"),
    thread_id: int = PathParam(..., ge=1),
    post_id: int = PathParam(..., ge=1),
) -> HTMLResponse:
    try:
        posts = await _load_thread_posts(board, thread_id)
    except HTTPStatusError as exc:
        status_code = exc.response.status_code
        message = (
            "Thread not found."
            if status_code == 404
            else "Unable to load thread right now."
        )
        return templates.TemplateResponse(
            "post_view.html",
            {
                "request": request,
                "screen": "post",
                "board": board,
                "error": message,
            },
            status_code=status_code,
        )
    except Exception:
        return templates.TemplateResponse(
            "post_view.html",
            {
                "request": request,
                "screen": "post",
                "board": board,
                "error": "Unable to load thread right now.",
            },
            status_code=502,
        )

    post = next((item for item in posts if item["no"] == post_id), None)
    if not post:
        return templates.TemplateResponse(
            "post_view.html",
            {
                "request": request,
                "screen": "post",
                "board": board,
                "error": "Post not found.",
            },
            status_code=404,
        )

    return templates.TemplateResponse(
        "post_view.html",
        {
            "request": request,
            "screen": "post",
            "board": board,
            "post": post,
        },
    )


@app.get(
    "/board/{board}/thread/{thread_id}/post/{post_id}/image",
    response_class=HTMLResponse,
)
async def post_image(
    request: Request,
    board: str = PathParam(..., pattern=r"^[a-z]{1,6}$"),
    thread_id: int = PathParam(..., ge=1),
    post_id: int = PathParam(..., ge=1),
) -> HTMLResponse:
    try:
        posts = await _load_thread_posts(board, thread_id)
    except HTTPStatusError as exc:
        status_code = exc.response.status_code
        message = (
            "Thread not found."
            if status_code == 404
            else "Unable to load thread right now."
        )
        return templates.TemplateResponse(
            "image_view.html",
            {
                "request": request,
                "screen": "image",
                "board": board,
                "error": message,
            },
            status_code=status_code,
        )
    except Exception:
        return templates.TemplateResponse(
            "image_view.html",
            {
                "request": request,
                "screen": "image",
                "board": board,
                "error": "Unable to load thread right now.",
            },
            status_code=502,
        )

    post = next((item for item in posts if item["no"] == post_id), None)
    if not post or not post.get("image_url"):
        return templates.TemplateResponse(
            "image_view.html",
            {
                "request": request,
                "screen": "image",
                "board": board,
                "error": "Image not available.",
            },
            status_code=404,
        )

    return templates.TemplateResponse(
        "image_view.html",
        {
            "request": request,
            "screen": "image",
            "board": board,
            "image_url": post["image_url"],
            "media_kind": post.get("media_kind", "file"),
            "file_name": post.get("file_name"),
            "file_size": post.get("file_size"),
        },
    )


def update() -> None:
    """Check for updates and install if available."""
    GREEN = "\033[38;2;67;227;39m"
    RESET = "\033[0m"

    print(f"{GREEN}→ Checking for updates...{RESET}")

    update_script = "https://raw.githubusercontent.com/htmlgxn/comfy-imageboard-explorer/main/scripts/update.sh"

    try:
        result = subprocess.run(
            ["bash", "-c", f"curl -sSL {update_script} | bash"],
            capture_output=False,
            text=True,
            check=False,
        )
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running update: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="imgboard-explorer",
        description="A TUI-style webapp for browsing imageboard content",
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["update"],
        help="Command to run (update: check for and install updates)",
    )

    args = parser.parse_args()

    if args.command == "update":
        update()
    else:
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
