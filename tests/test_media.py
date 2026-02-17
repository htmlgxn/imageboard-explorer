from imageboard_explorer.models import format_bytes, media_kind


def test_media_kind() -> None:
    assert media_kind(".jpg") == "image"
    assert media_kind(".JPeG") == "image"
    assert media_kind(".png") == "image"
    assert media_kind(".gif") == "image"
    assert media_kind(".webp") == "image"
    assert media_kind(".webm") == "video"
    assert media_kind(".mp4") == "video"
    assert media_kind(".zip") == "file"
    assert media_kind(None) == "file"


def test_format_bytes() -> None:
    assert format_bytes(None) is None
    assert format_bytes(0) == "0 B"
    assert format_bytes(512) == "512 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1536) == "1.5 KB"
    assert format_bytes(1024 * 1024) == "1.0 MB"
