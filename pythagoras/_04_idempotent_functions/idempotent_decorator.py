from typing import Callable

import logging

from pythagoras._03_autonomous_functions.default_island_singleton import (
    DefaultIslandType, DefaultIsland)

from pythagoras._04_idempotent_functions.idempotent_func_and_address import (
    IdempotentFunction)

from pythagoras._06_mission_control.global_state_management import (
    is_fully_unitialized)



class idempotent:

    island_name: str | None
    require_pth: bool

    def __init__(self
            , island_name: str | None |DefaultIslandType = DefaultIsland
            , require_pth: bool = True):
        assert (isinstance(island_name, str)
                or island_name is None
                or island_name is DefaultIsland)
        self.island_name = island_name
        self.require_pth = require_pth


    def __call__(self, a_func:Callable) -> IdempotentFunction:
        if not self.require_pth and is_fully_unitialized():
            wrapper = a_func
            logging.warning(f"Decorator @{self.__class__.__name__}()"
                + f" is used with function {a_func.__name__}"
                + " before Pythagoras is initialized."
                + " Pythagoras functionality is disabled for this function.")
        else:
            wrapper = IdempotentFunction(a_func, self.island_name)
        return wrapper

