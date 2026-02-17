import time

from imageboard_explorer.clients.chan_api import TTLCache


def test_cache_expires() -> None:
    cache = TTLCache()
    cache.set("key", {"ok": True}, ttl_seconds=0.01, last_modified=None)
    assert cache.get("key") is not None
    time.sleep(0.02)
    assert cache.get("key") is None


def test_cache_max_size() -> None:
    cache = TTLCache(max_size=3)
    cache.set("a", 1, ttl_seconds=60, last_modified=None)
    cache.set("b", 2, ttl_seconds=60, last_modified=None)
    cache.set("c", 3, ttl_seconds=60, last_modified=None)
    cache.set("d", 4, ttl_seconds=60, last_modified=None)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3
    assert cache.get("d") == 4


def test_cache_lru_eviction() -> None:
    cache = TTLCache(max_size=3)
    cache.set("a", 1, ttl_seconds=60, last_modified=None)
    cache.set("b", 2, ttl_seconds=60, last_modified=None)
    cache.set("c", 3, ttl_seconds=60, last_modified=None)
    cache.get("a")
    cache.set("d", 4, ttl_seconds=60, last_modified=None)
    assert cache.get("a") == 1
    assert cache.get("b") is None
    assert cache.get("c") == 3
    assert cache.get("d") == 4


def test_cache_expired_cleanup_on_set() -> None:
    cache = TTLCache(max_size=10)
    cache.set("a", 1, ttl_seconds=0.01, last_modified=None)
    time.sleep(0.02)
    cache.set("b", 2, ttl_seconds=60, last_modified=None)
    assert cache.get("a") is None
    assert cache.get("b") == 2
