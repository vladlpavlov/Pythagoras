from typing import Callable

from pythagoras import PortalAwareClass
from pythagoras._050_safe_functions.safe_core_classes import (
    SafeFn, SafeCodePortal)


class safe(PortalAwareClass):
    """A decorator that converts a Python function into an SafeFn object.
    """

    def __init__(self, portal: SafeCodePortal | None = None):
        PortalAwareClass.__init__(self=self, portal=portal)

    @property
    def portal(self) -> SafeCodePortal:
        return super().portal

    def __call__(self,a_func:Callable)->SafeFn:
        wrapper = SafeFn(a_func, portal=self.portal)
        return wrapper