from typing import Callable

from pythagoras._04_idempotent_functions.idempotent_func_address_context import (
    IdempotentFn, SupportingFuncs)


class idempotent:

    island_name: str | None

    def __init__(self
                 , island_name: str | None = None
                 , validators: SupportingFuncs = None
                 , correctors: SupportingFuncs = None):
        assert isinstance(island_name, str) or island_name is None
        self.island_name = island_name
        self.validators = validators
        self.correctors = correctors


    def __call__(self, a_func:Callable) -> IdempotentFn:
        wrapper = IdempotentFn(
            a_func
            , island_name = self.island_name
            , validators = self.validators
            , correctors = self.correctors)
        return wrapper

