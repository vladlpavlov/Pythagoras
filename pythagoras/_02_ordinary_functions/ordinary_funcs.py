from __future__ import annotations

from typing import Callable

from pythagoras import get_normalized_function_source


class OrdinaryFunction:

    def __init__(self, a_func: Callable | str | OrdinaryFunction):
        if isinstance(a_func, OrdinaryFunction):
            self.source_code = a_func.source_code
        else:
            self.source_code = get_normalized_function_source(a_func)

    def __call__(self, **kwargs):
        source_to_exec = self.source_code
        globals_dict = dict(globals())
        locals_dict = dict(locals())




