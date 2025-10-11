class Singleton(object):
    "A super class to all the class that needs to be singleton"

    def __new__(cls, *args, **kwargs):
        it = cls.__dict__.get("__it__")

        if it is not None:
            return it

        cls.__it__ = it = object.__new__(cls)

        it.init(*args, **kwargs)

        return it

    def init(self, *args, **kwargs):
        raise NotImplementedError(
            "This need to be implemented by the sub class for initialization and not __init__"
        )
