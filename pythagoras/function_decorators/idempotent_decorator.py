from typing import Optional
import pythagoras as pth
from functools import wraps
from pythagoras.python_utils.check_n_positional_args import (
    accepts_unlimited_positional_args)


class idempotent:
    def __init__(self, island_name:Optional[str]=None):
        assert pth.is_correctly_initialized()
        if island_name is None:
            island_name = pth.default_island_name
        self.island_name = island_name


    def __call__(self, a_func):
        assert not accepts_unlimited_positional_args(a_func)
        cloudized_function = pth.CloudizedFunction(a_func, self.island_name)

        @wraps(a_func)
        def wrapped_idempotant_function(**kwargs):
            return cloudized_function(**kwargs)
        wrapped_idempotant_function.__pth_cloudized_function__ = (
            cloudized_function)

        return wrapped_idempotant_function

