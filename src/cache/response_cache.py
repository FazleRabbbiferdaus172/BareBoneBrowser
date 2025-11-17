from src.cache.base_cache import Cache


class ResponseCache(Cache):
    "A class to cache the responses so that they can be reused"

    def init(self):
        super().init()

    def get(self, key: str) -> str | None:
        return self._cache.get(key, None)

    def set(self, key: str, value: str) -> None:
        self._cache[key] = value

    def invalidate_cache(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
