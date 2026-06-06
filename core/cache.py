"""
AI 响应缓存 — TTL 缓存层，节省 API 调用费用
对相同 query + feature 的组合缓存 1 小时
"""
import hashlib
import json
import os
import time
from collections import OrderedDict

CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ai_cache.json')


class AICache:
    """LRU + TTL 缓存（支持持久化）"""

    def __init__(self, max_size: int = 200, ttl_seconds: int = 3600):
        self._cache = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0
        self._load()

    def _make_key(self, messages: list, feature: str) -> str:
        """生成缓存键"""
        raw = json.dumps(messages, ensure_ascii=False, sort_keys=True) + feature
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, messages: list, feature: str) -> str | None:
        """获取缓存的响应，过期返回 None"""
        key = self._make_key(messages, feature)
        if key not in self._cache:
            self._misses += 1
            return None

        entry = self._cache[key]
        if time.time() - entry["ts"] > self._ttl:
            del self._cache[key]
            self._misses += 1
            return None

        # Move to end (LRU)
        self._cache.move_to_end(key)
        self._hits += 1
        return entry["response"]

    def set(self, messages: list, feature: str, response: str):
        """存入缓存"""
        key = self._make_key(messages, feature)
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = {"response": response, "ts": time.time()}
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def _load(self):
        """从磁盘恢复缓存"""
        if not os.path.exists(CACHE_FILE):
            return
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            now = time.time()
            loaded = 0
            for key, entry in data.get('entries', {}).items():
                if now - entry.get('ts', 0) < self._ttl:
                    self._cache[key] = entry
                    loaded += 1
            self._hits = data.get('hits', 0)
            self._misses = data.get('misses', 0)
        except (json.JSONDecodeError, OSError):
            pass

    def save(self):
        """持久化缓存到磁盘"""
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        try:
            data = {
                'entries': dict(self._cache),
                'hits': self._hits,
                'misses': self._misses,
            }
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except OSError:
            pass

    def clear(self):
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    @property
    def stats(self) -> dict:
        total = self._hits + self._misses
        hit_rate = self._hits / total * 100 if total > 0 else 0
        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.0f}%",
        }


# 全局缓存单例
_cache = AICache()


def get_cache() -> AICache:
    return _cache
