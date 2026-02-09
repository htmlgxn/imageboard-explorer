from pydantic import BaseModel


class Board(BaseModel):
    board: str
    title: str
    ws_board: int
    pages: int
    per_page: int
    meta_description: str | None = None


class CatalogThread(BaseModel):
    no: int
    now: str | None = None
    time: int | None = None
    name: str | None = None
    sub: str | None = None
    com: str | None = None
    replies: int | None = None
    images: int | None = None
    tim: int | None = None
    ext: str | None = None
    country: str | None = None
    country_name: str | None = None


class ThreadPost(BaseModel):
    no: int
    resto: int = 0
    now: str | None = None
    time: int | None = None
    name: str | None = None
    com: str | None = None
    tim: int | None = None
    ext: str | None = None
    filename: str | None = None
    fsize: int | None = None
    country: str | None = None
    country_name: str | None = None


class Thread(BaseModel):
    posts: list[ThreadPost]


def thumbnail_url(board: str, tim: int | None) -> str | None:
    if not tim:
        return None
    return f"https://i.4cdn.org/{board}/{tim}s.jpg"


def image_url(board: str, tim: int | None, ext: str | None) -> str | None:
    if not tim or not ext:
        return None
    return f"https://i.4cdn.org/{board}/{tim}{ext}"


IMAGE_EXTS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".avif",
    ".svg",
    ".bmp",
    ".tif",
    ".tiff",
}
VIDEO_EXTS = {".webm", ".mp4", ".m4v", ".ogv"}


def media_kind(ext: str | None) -> str:
    if not ext:
        return "file"
    ext_lower = ext.lower()
    if ext_lower in IMAGE_EXTS:
        return "image"
    if ext_lower in VIDEO_EXTS:
        return "video"
    return "file"


def format_bytes(value: int | None) -> str | None:
    if value is None:
        return None
    size = float(value)
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return None


def country_flag_url(country_code: str | None) -> str | None:
    """Generate country flag URL from country code."""
    if not country_code:
        return None
    return f"https://s.4cdn.org/image/country/{country_code.lower()}.gif"
