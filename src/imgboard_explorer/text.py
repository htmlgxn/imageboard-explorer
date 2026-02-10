import html
import re
from typing import Optional
from urllib.parse import urlparse

_BR_RE = re.compile(r"(<br\s*/?>)+", re.IGNORECASE)
_QUOTELINK_RE = re.compile(r'<a[^>]*class="quotelink"[^>]*>(.*?)</a>', re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_QUOTE_MARK_RE = re.compile(r"&gt;&gt;(\d+)")
_QUOTE_TEXT_RE = re.compile(r">>(\d+)")
_URL_RE = re.compile(r"(https?://[^\s<]+[^.,!?;:\s<])")


def _is_safe_url(url: str) -> bool:
    """Validate URL scheme to prevent XSS via javascript: URLs."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https")
    except Exception:
        return False


def html_to_text(raw: Optional[str]) -> str:
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
    # Use placeholders to handle URLs and quotes before HTML escaping
    # to avoid issues with escaped characters (like & and ;) being matched/broken.
    placeholders: list[str] = []

    def add_placeholder(token: str, is_quote: bool) -> str:
        idx = len(placeholders)
        if is_quote:
            # token is just the quote ID
            placeholders.append(
                f'<span class="nav-link link-quote" data-quote-id="{token}">&gt;&gt;{token}</span>'
            )
        else:
            # token is the full URL
            escaped_url = html.escape(token)
            placeholders.append(
                f'<span class="nav-link link-external" data-url="{escaped_url}">{escaped_url}</span>'
            )
        return f"__PH_{idx}__"

    combined_re = re.compile(f"({_URL_RE.pattern}|{_QUOTE_TEXT_RE.pattern})")

    def replace_token(match: re.Match[str]) -> str:
        token = match.group(0)
        url_match = _URL_RE.fullmatch(token)
        if url_match and _is_safe_url(url_match.group(1)):
            return add_placeholder(token, False)

        quote_match = _QUOTE_TEXT_RE.fullmatch(token)
        if quote_match:
            return add_placeholder(quote_match.group(1), True)

        return token

    # 1. Identify and replace with placeholders in raw text
    processed = combined_re.sub(replace_token, text)

    # 2. Escape the rest of the text and convert newlines
    escaped = html.escape(processed)
    escaped = escaped.replace("\n", "<br>")

    # 3. Restore placeholders
    for i, ph_content in enumerate(placeholders):
        escaped = escaped.replace(f"__PH_{i}__", ph_content)

    return escaped
