import pythagoras as pth

from pythagoras._03_autonomous_functions.default_island_singleton import (
    DefaultIslandType, DefaultIsland)

from pythagoras._04_idempotent_functions.idempotent_func_and_address import (
    IdempotentFunction)



class idempotent:
    def __init__(self, island_name: str | None |DefaultIslandType = None,**_):
        # assert pth.is_correctly_initialized()
        assert (isinstance(island_name, str)
                or island_name is None
                or island_name is DefaultIsland)
        if isinstance(island_name, str):
            assert island_name in pth.get_all_island_names()
        self.island_name = island_name


    def __call__(self, a_func):
        wrapper = IdempotentFunction(a_func, self.island_name)
        return wrapper

