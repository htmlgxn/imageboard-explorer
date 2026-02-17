from imageboard_explorer.models import country_flag_url, image_url, thumbnail_url


def test_thumbnail_url() -> None:
    assert thumbnail_url("a", 1234) == "https://i.4cdn.org/a/1234s.jpg"
    assert thumbnail_url("a", None) is None


def test_image_url() -> None:
    assert image_url("b", 5678, ".jpg") == "https://i.4cdn.org/b/5678.jpg"
    assert image_url("b", None, ".jpg") is None
    assert image_url("b", 5678, None) is None


def test_country_flag_url() -> None:
    assert country_flag_url("US") == "https://s.4cdn.org/image/country/us.gif"
    assert country_flag_url("us") == "https://s.4cdn.org/image/country/us.gif"
    assert country_flag_url("UK") == "https://s.4cdn.org/image/country/uk.gif"
    assert country_flag_url(None) is None
    assert country_flag_url("") is None
