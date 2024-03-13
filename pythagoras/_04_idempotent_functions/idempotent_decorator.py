from typing import Callable

import logging

from pythagoras._04_idempotent_functions.idempotent_func_address_context import (
    IdempotentFunction)


class idempotent:

    island_name: str | None

    def __init__(self, island_name: str | None = None):
        assert isinstance(island_name, str) or island_name is None
        self.island_name = island_name


    def __call__(self, a_func:Callable) -> IdempotentFunction:
        wrapper = IdempotentFunction(a_func, self.island_name)
        return wrapper

