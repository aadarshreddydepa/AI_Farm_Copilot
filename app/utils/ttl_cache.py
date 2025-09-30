# backend/app/utils/ttl_cache.py
import time
from typing import Any

class TTLCache:
    def __init__(self, default_ttl_seconds: int = 300):
        self._store: dict[str, tuple[float, Any]] = {}
        self._ttl = default_ttl_seconds

    def get(self, key: str):
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None):
        ttl = ttl if ttl is not None else self._ttl
        self._store[key] = (time.time() + ttl, value)

    def clear(self):
        self._store.clear()
