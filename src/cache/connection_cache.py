import socket
from src.utils.cache import Cache


# Todo: write tests for class
class ConnectionCache(Cache):
    "A class to cache the socket so that it can be reused"

    def init(self):
        self._connections: dict[str, socket.socket] = {}

    def get(self, host_name: str):
        return self._connections.get(host_name, None)

    def set(self, host_name: str, sc: socket.socket):
        self._connections[host_name] = sc

    def _close_socket(self, host_name):
        self._connections[host_name].close()

    def remove(self, host_name: str):
        if host_name in self._connections:
            self._close_socket(host_name)
            del self._connections[host_name]
            return True
        return False

    def invalidate_cache(self, host_name: str):
        if host_name in self._connections:
            self._close_socket(host_name)
            del self._connections[host_name]
            return True
        return False
