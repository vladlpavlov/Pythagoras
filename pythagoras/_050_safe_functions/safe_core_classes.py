from __future__ import annotations

from typing import Callable

from persidict import FileDirDict, PersiDict

from pythagoras import BasicPortal
from pythagoras._040_ordinary_functions.ordinary_core_classes import (
    OrdinaryFn, OrdinaryCodePortal)


class SafeCodePortal(OrdinaryCodePortal):
    def __init__(self
                 , root_dict: PersiDict | str | None = None
                 , p_consistency_checks: float | None = None
                 ):
        super().__init__(root_dict=root_dict
            , p_consistency_checks=p_consistency_checks)


    @classmethod
    def get_best_portal_to_use(cls, suggested_portal: SafeCodePortal | None = None
                               ) -> OrdinaryCodePortal:
        return BasicPortal.get_best_portal_to_use(suggested_portal)

    @classmethod
    def get_most_recently_entered_portal(cls) -> SafeCodePortal | None:
        """Get the current portal object"""
        return BasicPortal._most_recently_entered_portal(expected_class=cls)

    @classmethod
    def get_noncurrent_portals(cls) -> list[SafeCodePortal]:
        """Get all portals except the most recently entered one"""
        return BasicPortal._noncurrent_portals(expected_class=cls)

    @classmethod
    def get_entered_portals(cls) -> list[SafeCodePortal]:
        return BasicPortal._entered_portals(expected_class=cls)

class SafeFn(OrdinaryFn):
    def __init__(self
                 , a_func: Callable | str | SafeFn
                 , portal: OrdinaryCodePortal | None = None
                 , **_):
        OrdinaryFn.__init__(self, a_func = a_func, portal=portal, **_)
        if isinstance(a_func, SafeFn):
            self.update(a_func)
            return

    @property
    def decorator(self):
        return "@pth.safe()"

    @property
    def portal(self) -> SafeCodePortal:
        return super().portal

    def _complete_fn_registration(self):
        OrdinaryFn._complete_fn_registration(self)
        if type(self) == SafeFn:
            self._fn_fully_registered = True