"""In-memory sliding-window rate limiter for local development.

Production note:
Replace this in-process limiter with a distributed store (such as Redis) or an
API gateway rate limiter when deploying multiple HelpBot worker processes.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from app.core.exceptions import RateLimitExceededError


class InMemoryRateLimiter:
    """Thread-safe per-key sliding-window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int = 60) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._buckets: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - self._window_seconds
        with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= self._max_requests:
                raise RateLimitExceededError()
            bucket.append(now)

    def reset(self) -> None:
        with self._lock:
            self._buckets.clear()
