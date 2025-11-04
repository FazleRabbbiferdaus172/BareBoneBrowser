from src.cache.response_cache import ResponseCache


def cache_response(func):
    def wrapper(self, *args, **kwargs):
        print("hello from decorator")
        response_cache = ResponseCache()
        key = self.scheme + "://" + self.host + ":" + str(self.port) + self.path
        response = response_cache.get(key)
        if not response:
            response = func(self, *args, **kwargs)
        response_cache.set(key, response)
        return response_cache.get(key)

    return wrapper
