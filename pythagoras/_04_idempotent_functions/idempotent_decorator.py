from typing import Callable

from pythagoras._05_mission_control.global_state_management import (
    is_correctly_initialized)

from pythagoras._03_autonomous_functions.default_island_singleton import (
    DefaultIslandType, DefaultIsland)

from pythagoras._04_idempotent_functions.idempotent_func_and_address import (
    IdempotentFunction)



class idempotent:

    island_name: str | None

    def __init__(self
            , island_name: str | None |DefaultIslandType = DefaultIsland):
        assert (isinstance(island_name, str)
                or island_name is None
                or island_name is DefaultIsland)
        self.island_name = island_name


    def __call__(self, a_func:Callable) -> Callable:
        wrapper = IdempotentFunction(a_func, self.island_name)
        return wrapper

