from src.cache.base_cache import Cache
from tkinter.font import Font
from tkinter import Label

class FontCache(Cache):
    "A cache class for font objects"

    def default_set(self, size: int, weight: int, style: str) -> Font:
        "A default get method that returns None if the font is not found in the cache"
        font = Font(size=size, weight=weight, slant=style)
        label = Label(font=font)
        self.set(size, weight, style,font, label)

    def get(self, size: int, weight: int, style: str) -> Font:
        "Get the font object from the cache if it exists, otherwise return None"
        key = (size, weight, style)
        if key not in self._cache:
            self.default_set(size, weight, style)
        return self._cache.get((size, weight, style))[0]

    def set(self, size: int, weight: int, style: str, font: Font, label: Label):
        "Set the font object in the cache with the given font name and size"
        self._cache[(size, weight, style)] = (font, label)

    def invalidate_cache(self, size: str|None = None, weight: str | None= None):
        "Invalidate the cache for a specific font name and size or clear all if both are None"
        if size is not None and weight is not None:
            self._cache.pop((size, weight), None)
        elif size is not None:
            keys_to_remove = [key for key in self._cache if key[0] == size]
            for key in keys_to_remove:
                self._cache.pop(key, None)
        elif weight is not None:
            keys_to_remove = [key for key in self._cache if key[1] == weight]
            for key in keys_to_remove:
                self._cache.pop(key, None)