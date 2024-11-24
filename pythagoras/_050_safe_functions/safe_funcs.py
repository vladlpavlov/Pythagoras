from __future__ import annotations

from typing import Callable

from pythagoras._040_ordinary_functions.ordinary_funcs import OrdinaryFn

class SafeFn(OrdinaryFn):
    def __init__(self, a_func: Callable | str | SafeFn, **_):
        OrdinaryFn.__init__(self, a_func, **_)

    def _complete_fn_registration(self):
        OrdinaryFn._complete_fn_registration(self)
        if type(self) == SafeFn:
            self._fn_fully_registered = True