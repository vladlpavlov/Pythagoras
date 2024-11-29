from typing import Callable

from pythagoras import PortalAwareClass
from pythagoras._040_ordinary_functions.ordinary_core_classes import (
    OrdinaryFn, OrdinaryCodePortal)


class ordinary(PortalAwareClass):
    """A decorator that converts a Python function into an OrdinaryFn object.

    As a part of the conversion process, the source code of the function
    is checked. If it does not meet the requirements of an ordinary function,
    an exception is raised.
    """

    def __init__(self, portal: OrdinaryCodePortal | None = None):
        PortalAwareClass.__init__(self=self, portal=portal)

    @property
    def portal(self) -> OrdinaryCodePortal:
        return super().portal

    def __call__(self,a_func:Callable)->OrdinaryFn:
        wrapper = OrdinaryFn(a_func, portal=self.portal)
        return wrapper