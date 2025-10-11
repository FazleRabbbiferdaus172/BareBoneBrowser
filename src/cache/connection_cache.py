import socket
from src.utils.singleton import Singleton

class ConnectionCache(Singleton):
    "A class to cache the socket so that it can be reused"
    def init(self):
        self._connections: dict[str, socket.socket ] = {}

    def get(self, host_name: str):
        return self._connections.get(host_name, None)
    
    def set(self, host_name: str, sc : socket.socket):
        self._connections[host_name] = sc

    def remove(self, host_name: str):
        if host_name in self._connections:
            del self._connections[host_name]
            return True
        return False

    def invalidate_cache(self, host_name: str):
        if host_name in self._connections:
            del self._connections[host_name]
            return True
        return False

