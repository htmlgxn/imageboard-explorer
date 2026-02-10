import asyncio
import json
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional

import httpx


@dataclass
class CacheEntry:
    data: Any
    expires_at: float
    last_modified: Optional[str]


class TTLCache:
    def __init__(self, max_size: int = 100) -> None:
        self._entries: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        entry = self._entries.get(key)
        if not entry:
            return None
        if entry.expires_at <= time.monotonic():
            return None
        # Move to end (most recently used)
        self._entries.move_to_end(key)
        return entry.data

    def get_entry(self, key: str) -> Optional[CacheEntry]:
        entry = self._entries.get(key)
        if entry:
            self._entries.move_to_end(key)
        return entry

    def set(
        self, key: str, data: Any, ttl_seconds: float, last_modified: Optional[str]
    ) -> None:
        # Evict oldest if at capacity and we're adding a new key
        if key not in self._entries and len(self._entries) >= self._max_size:
            self._entries.popitem(last=False)

        self._entries[key] = CacheEntry(
            data=data,
            expires_at=time.monotonic() + ttl_seconds,
            last_modified=last_modified,
        )

    def refresh(self, key: str, ttl_seconds: float) -> None:
        entry = self._entries.get(key)
        if entry:
            entry.expires_at = time.monotonic() + ttl_seconds


class RateLimiter:
    def __init__(self, interval_seconds: float) -> None:
        self._interval = interval_seconds
        self._lock = asyncio.Lock()
        self._last_request_at = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request_at
            if elapsed < self._interval:
                await asyncio.sleep(self._interval - elapsed)
            self._last_request_at = time.monotonic()


class ChanAPIClient:
    def __init__(
        self, base_url: str = "https://a.4cdn.org", timeout: float = 10.0
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._cache = TTLCache()
        self._rate_limiter = RateLimiter(interval_seconds=1.0)

    async def start(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def fetch_json(self, path: str, ttl_seconds: float) -> Any:
        if self._client is None:
            await self.start()
        assert self._client is not None
        url = f"{self.base_url}/{path.lstrip('/')}"
        cached = self._cache.get(url)
        if cached is not None:
            return cached

        entry = self._cache.get_entry(url)
        headers = {}
        if entry and entry.last_modified:
            headers["If-Modified-Since"] = entry.last_modified

        await self._rate_limiter.wait()
        response = await self._client.get(url, headers=headers)
        if response.status_code == 304 and entry:
            self._cache.refresh(url, ttl_seconds)
            return entry.data

        response.raise_for_status()
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise httpx.HTTPError(f"Invalid JSON response from {url}") from e
        last_modified = response.headers.get("Last-Modified")
        self._cache.set(url, data, ttl_seconds, last_modified)
        return data
