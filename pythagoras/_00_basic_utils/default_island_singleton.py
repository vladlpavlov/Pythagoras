class DefaultIslandType:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DefaultIslandType, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __repr__(self):
        return "DefaultIsland"

DefaultIsland = DefaultIslandType()