# -*- coding: utf-8 -*-
"""简单进程内滑动窗口限流（单机部署够用）。"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from app.schema import BaseAppException

_lock = threading.Lock()
_buckets: dict[str, deque[float]] = defaultdict(deque)


def check_rate_limit(key: str, *, limit: int, window_seconds: int, error_code: str = "RATE_LIMITED") -> None:
    """超过限制则抛业务异常。"""
    now = time.time()
    cutoff = now - window_seconds
    with _lock:
        q = _buckets[key]
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) >= limit:
            raise BaseAppException(message="too many requests", error_code=error_code)
        q.append(now)


def seen_recently(key: str, *, window_seconds: int) -> bool:
    """若 key 在窗口内已出现过则返回 True，否则记一次并返回 False。"""
    now = time.time()
    cutoff = now - window_seconds
    with _lock:
        q = _buckets[key]
        while q and q[0] < cutoff:
            q.popleft()
        if q:
            return True
        q.append(now)
        return False
