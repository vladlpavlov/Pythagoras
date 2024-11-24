from typing import Callable

from pythagoras._060_autonomous_functions.autonomous_core_classes import (
    PortalAwareClass)
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal, PureFn, SupportingFuncs)



class pure(PortalAwareClass):

    island_name: str | None
    guardians: SupportingFuncs

    def __init__(self
                 , island_name: str | None = None
                 , guards: SupportingFuncs = None
                 , portal:PureCodePortal | None = None ):
        assert isinstance(island_name, str) or island_name is None
        self.island_name = island_name
        self.guards = guards
        super().__init__(portal=portal)

    @property
    def portal(self) -> PureCodePortal:
        return super().portal


    def __call__(self, a_func:Callable) -> PureFn:
        with self.portal:
            wrapper = PureFn(
                a_func
                , island_name = self.island_name
                , guards= self.guards
                , portal = self.portal)
            return wrapper

