import socket
from src.cache.base_cache import Cache


# Todo: write tests for class
class ConnectionCache(Cache):
    "A class to cache the socket so that it can be reused"

    def init(self):
        super().init()
        # self._cache: dict[str, socket.socket] = {}

    def get(self, host_name: str):
        return self._cache.get(host_name, None)

    def set(self, host_name: str, sc: socket.socket):
        self._cache[host_name] = sc

    def _close_socket(self, host_name):
        self._cache[host_name].close()

    def remove(self, host_name: str):
        if host_name in self._cache:
            self._close_socket(host_name)
            del self._cache[host_name]
            return True
        return False

    def invalidate_cache(self, host_name: str):
        if host_name in self._cache:
            self._close_socket(host_name)
            del self._cache[host_name]
            return True
        return False
