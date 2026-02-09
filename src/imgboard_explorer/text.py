import html
import re
from urllib.parse import urlparse

_BR_RE = re.compile(r"(<br\s*/?>)+", re.IGNORECASE)
_QUOTELINK_RE = re.compile(r'<a[^>]*class="quotelink"[^>]*>(.*?)</a>', re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_QUOTE_MARK_RE = re.compile(r"&gt;&gt;(\d+)")
_QUOTE_TEXT_RE = re.compile(r">>(\d+)")
_URL_RE = re.compile(r"(https?://[^\s<]+)")


def _is_safe_url(url: str) -> bool:
    """Validate URL scheme to prevent XSS via javascript: URLs."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https")
    except Exception:
        return False


def html_to_text(raw: str | None) -> str:
    if not raw:
        return ""
    text = raw.replace("<wbr>", "")
    text = _BR_RE.sub("\n", text)
    text = _QUOTELINK_RE.sub(r"\1", text)
    text = _TAG_RE.sub("", text)
    text = html.unescape(text)
    return text.strip()


def extract_quotes(text: str) -> tuple[list[str], list[str]]:
    if not text:
        return [], []

    lines = text.splitlines()
    header_quotes: list[str] = []
    body_quotes: list[str] = []
    index = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            index += 1
            continue
        quote_matches = _QUOTE_TEXT_RE.findall(stripped)
        if not quote_matches:
            break
        remainder = _QUOTE_TEXT_RE.sub("", stripped).strip()
        if remainder:
            break
        header_quotes.extend(quote_matches)
        index += 1

    for line in lines[index:]:
        body_quotes.extend(_QUOTE_TEXT_RE.findall(line))

    return header_quotes, body_quotes


def extract_all_quotes(text: str) -> list[str]:
    if not text:
        return []
    return _QUOTE_TEXT_RE.findall(text)


def strip_header_quotes(text: str) -> str:
    if not text:
        return ""

    lines = text.splitlines()
    remaining: list[str] = []
    skipping = True

    for line in lines:
        if skipping:
            stripped = line.strip()
            if not stripped:
                continue
            quote_matches = _QUOTE_TEXT_RE.findall(stripped)
            if quote_matches and not _QUOTE_TEXT_RE.sub("", stripped).strip():
                continue
            skipping = False
        remaining.append(line)

    return "\n".join(remaining).lstrip()


def text_to_html(text: str) -> str:
    escaped = html.escape(text)
    escaped = escaped.replace("\n", "<br>")
    escaped = _QUOTE_MARK_RE.sub(
        r'<span class="nav-link link-quote" data-quote-id="\1">&gt;&gt;\1</span>',
        escaped,
    )

    def replace_url(match: re.Match[str]) -> str:
        url = match.group(1)
        if _is_safe_url(url):
            return f'<span class="nav-link link-external" data-url="{url}">{url}</span>'
        return url

    escaped = _URL_RE.sub(replace_url, escaped)
    return escaped
