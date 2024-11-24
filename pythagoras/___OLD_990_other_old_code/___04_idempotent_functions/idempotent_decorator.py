from typing import Callable

from pythagoras.___03_OLD_autonomous_functions.autonomous_funcs import (
    CodePortal, PortalAwareClass)
from pythagoras.___04_idempotent_functions.idempotent_func_address_context import (
    IdempotentFn, SupportingFuncs)



class idempotent(PortalAwareClass):

    island_name: str | None

    def __init__(self
                 , island_name: str | None = None
                 , validators: SupportingFuncs = None
                 , correctors: SupportingFuncs = None
                 , portal:CodePortal | None = None ):
        assert isinstance(island_name, str) or island_name is None
        self.island_name = island_name
        self.validators = validators
        self.correctors = correctors
        super().__init__(portal=portal)

    @property
    def portal(self) -> CodePortal:
        return super().portal


    def __call__(self, a_func:Callable) -> IdempotentFn:
        with self.portal:
            wrapper = IdempotentFn(
                a_func
                , island_name = self.island_name
                , validators = self.validators
                , correctors = self.correctors
                , portal = self.portal)
            return wrapper

