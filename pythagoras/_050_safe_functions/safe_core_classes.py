from __future__ import annotations

from typing import Callable

from persidict import FileDirDict

from pythagoras import BasicPortal
from pythagoras._040_ordinary_functions.ordinary_core_classes import (
    OrdinaryFn, OrdinaryCodePortal)


class SafeCodePortal(OrdinaryCodePortal):
    def __init__(
            self
            , base_dir: str | None = None
            , dict_type: type = FileDirDict
            , p_consistency_checks: float | None = None
            ):
        super().__init__(base_dir=base_dir
            , dict_type=dict_type
            , p_consistency_checks=p_consistency_checks)


    @classmethod
    def get_portal(cls, suggested_portal: SafeCodePortal | None = None
                   ) -> OrdinaryCodePortal:
        return BasicPortal.get_portal(suggested_portal)

    @classmethod
    def get_current_portal(cls) -> SafeCodePortal | None:
        """Get the current (default) portal object"""
        return BasicPortal._current_portal(expected_class=cls)

    @classmethod
    def get_noncurrent_portals(cls) -> list[SafeCodePortal]:
        return BasicPortal._noncurrent_portals(expected_class=cls)

    @classmethod
    def get_active_portals(cls) -> list[SafeCodePortal]:
        return BasicPortal._active_portals(expected_class=cls)

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