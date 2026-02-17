from imageboard_explorer.text import (
    extract_all_quotes,
    extract_quotes,
    html_to_text,
    strip_header_quotes,
    text_to_html,
)


def test_html_to_text_strips_tags_and_br() -> None:
    raw = "Hello<br>World <b>bold</b> &amp; stuff"
    assert html_to_text(raw) == "Hello\nWorld bold & stuff"


def test_text_to_html_wraps_quotes() -> None:
    text = ">>123456 hello"
    rendered = text_to_html(text)
    assert 'data-quote-id="123456"' in rendered


def test_extract_quotes_header_and_body() -> None:
    text = ">>1111 >>2222\n>>3333\nHello >>4444 world\n>>5555"
    header, body = extract_quotes(text)
    assert header == ["1111", "2222", "3333"]
    assert body == ["4444", "5555"]


def test_strip_header_quotes() -> None:
    text = ">>1111\n>>2222\nHello >>3333"
    assert strip_header_quotes(text) == "Hello >>3333"


def test_extract_all_quotes() -> None:
    text = "hi >>1111 there >>2222\n>>3333"
    assert extract_all_quotes(text) == ["1111", "2222", "3333"]
