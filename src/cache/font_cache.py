from src.cache.base_cache import Cache
from tkinter.font import Font

class FontCache(Cache):
    "A cache class for font objects"

    def get(self, font_name: str, font_size: int) -> Font:
        "Get the font object from the cache if it exists, otherwise return None"
        return self._cache.get((font_name, font_size))

    def set(self, font_name: str, font_size: int, font_object: Font):
        "Set the font object in the cache with the given font name and size"
        self._cache[(font_name, font_size)] = font_object

    def invalidate_cache(self, font_name: str|None = None, font_size: str | None= None):
        "Invalidate the cache for a specific font name and size or clear all if both are None"
        if font_name is not None and font_size is not None:
            self._cache.pop((font_name, font_size), None)
        elif font_name is not None:
            keys_to_remove = [key for key in self._cache if key[0] == font_name]
            for key in keys_to_remove:
                self._cache.pop(key, None)
        elif font_size is not None:
            keys_to_remove = [key for key in self._cache if key[1] == font_size]
            for key in keys_to_remove:
                self._cache.pop(key, None)