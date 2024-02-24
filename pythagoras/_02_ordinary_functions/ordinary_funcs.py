from __future__ import annotations

from typing import Callable
from pythagoras._00_basic_utils.function_name import (
    get_function_name_from_source)
from pythagoras._02_ordinary_functions.code_normalizer_implementation import (
    __get_normalized_function_source__)


class OrdinaryFunction:
    naked_source_code:str
    name:str

    def __init__(self, a_func: Callable | str | OrdinaryFunction, **_):
        if isinstance(a_func, OrdinaryFunction):
            self.naked_source_code = a_func.naked_source_code
            self.name = a_func.name
        else:
            assert callable(a_func) or isinstance(a_func, str)
            self.naked_source_code = __get_normalized_function_source__(
                a_func, drop_pth_decorators=True)
            self.name = get_function_name_from_source(self.naked_source_code)

    def _call_naked_code(self, **kwargs):
        names_dict = dict(globals())
        names_dict.update(locals())
        names_dict["__pth_kwargs"] = kwargs
        source_to_exec = self.naked_source_code
        source_to_exec += f"\n__pth_result = {self.name}(**__pth_kwargs)\n"
        exec(source_to_exec, names_dict, names_dict)
        result = names_dict["__pth_result"]
        return result

    def __call__(self, **kwargs):
        return self._call_naked_code(**kwargs)

    @property
    def decorator(self):
        return "@pth.ordinary()"






