from src.utils.singleton import Singleton

class Cache(Singleton):
    "A super class to all the cache classes"

    def init(self):
        raise NotImplementedError(
            "This need to be implemented by the sub class for initialization and not __init__"
        )

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
        raise NotImplementedError(
            "This need to be implemented by the sub class for clearing cache"
        )