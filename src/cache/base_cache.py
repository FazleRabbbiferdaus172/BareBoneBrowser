from src.utils.singleton import Singleton


class Cache(Singleton):
    "A super class to all the cache classes"

    def init(self):
        self._cache = dict()

    def get(self, *args, **kwargs):
        raise NotImplementedError(
            "This need to be implemented by the sub class for getting cache"
        )

    def set(self, *args, **kwargs):
        raise NotImplementedError(
            "This need to be implemented by the sub class for getting cache"
        )

    def invalidate_cache(self, *args, **kwargs):
        raise NotImplementedError(
            "This need to be implemented by the sub class for invalidating cache"
        )

    def clear_cache(self, *args, **kwargs):
        self._cache.clear()
