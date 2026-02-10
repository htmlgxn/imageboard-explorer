from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import HTTPStatusError, Response

from imgboard_explorer.main import app

client = TestClient(app)


@pytest.fixture
def mock_chan_api() -> Generator[MagicMock, None, None]:
    with patch("imgboard_explorer.main.client") as mock:
        yield mock


def test_home_route(mock_chan_api: MagicMock) -> None:
    mock_chan_api.fetch_json = AsyncMock(
        return_value={
            "boards": [
                {
                    "board": "v",
                    "title": "Video Games",
                    "ws_board": 1,
                    "pages": 10,
                    "per_page": 15,
                }
            ]
        }
    )
    response = client.get("/")
    assert response.status_code == 200
    assert "Video Games" in response.text
    assert "/v/" in response.text


def test_catalog_route(mock_chan_api: MagicMock) -> None:
    mock_chan_api.fetch_json = AsyncMock(
        return_value=[
            {
                "threads": [
                    {
                        "no": 123,
                        "sub": "Thread Subject",
                        "com": "Thread Comment",
                        "replies": 5,
                        "images": 1,
                    }
                ]
            }
        ]
    )
    response = client.get("/board/v/catalog")
    assert response.status_code == 200
    assert "Thread Subject" in response.text
    assert "No.123" in response.text


def test_thread_route(mock_chan_api: MagicMock) -> None:
    mock_chan_api.fetch_json = AsyncMock(
        return_value={
            "posts": [
                {"no": 123, "com": "OP post", "now": "02/10/26(Tue)12:00:00"},
                {"no": 124, "com": ">>123 reply", "now": "02/10/26(Tue)12:01:00"},
            ]
        }
    )
    response = client.get("/board/v/thread/123")
    assert response.status_code == 200
    assert "OP post" in response.text
    assert "No.123" in response.text
    assert "No.124" in response.text


def test_post_view_route(mock_chan_api: MagicMock) -> None:
    mock_chan_api.fetch_json = AsyncMock(
        return_value={
            "posts": [
                {
                    "no": 123,
                    "com": "OP post",
                    "now": "02/10/26(Tue)12:00:00",
                    "tim": 12345,
                    "ext": ".jpg",
                    "filename": "test",
                }
            ]
        }
    )
    response = client.get("/board/v/thread/123/post/123")
    assert response.status_code == 200
    assert "OP post" in response.text
    assert "12345.jpg" in response.text


def test_board_not_found(mock_chan_api: MagicMock) -> None:
    mock_chan_api.fetch_json.side_effect = HTTPStatusError(
        "Not Found", request=AsyncMock(), response=Response(404)
    )
    response = client.get("/board/zzzz/catalog")
    assert response.status_code == 404
    assert "Board /zzzz/ not found" in response.text
