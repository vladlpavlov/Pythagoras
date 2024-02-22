from typing import Optional
import pythagoras as pth
from functools import wraps
from pythagoras._02_ordinary_functions.check_n_positional_args import (
    accepts_unlimited_positional_args)


class idempotent:
    def __init__(self, island_name:Optional[str]=None):
        assert pth.is_correctly_initialized()
        if island_name is None:
            island_name = pth.default_island_name
        self.island_name = island_name


    def __call__(self, a_func):
        assert not accepts_unlimited_positional_args(a_func)
        idempotent_function = pth.IdempotentFunction(a_func, self.island_name)

        @wraps(a_func)
        def wrapped_idempotant_function(**kwargs):
            return idempotent_function(**kwargs)
        wrapped_idempotant_function.__pth_cloudized_function__ = (
            idempotent_function)

        return wrapped_idempotant_function

