from __future__ import annotations

from typing import Callable


from pythagoras._02_ordinary_functions.function_name import (
    get_function_name_from_source)
from pythagoras._02_ordinary_functions.code_normalizer_implementation import (
    __get_normalized_function_source__)


class OrdinaryFn:
    fn_source_code:str
    fn_name:str

    def __init__(self, a_func: Callable | str | OrdinaryFn, **_):

        if isinstance(a_func, OrdinaryFn):
            self.fn_source_code = a_func.fn_source_code
            self.fn_name = a_func.fn_name
        else:
            assert callable(a_func) or isinstance(a_func, str)
            self.fn_source_code = __get_normalized_function_source__(
                a_func, drop_pth_decorators=True)
            self.fn_name = get_function_name_from_source(self.fn_source_code)


    def __call__(self,*args, **kwargs):
        assert len(args) == 0, (f"Function {self.fn_name} can't"
            + " be called with positional arguments,"
            + " only keyword arguments are allowed.")
        names_dict = dict(globals())
        names_dict.update(locals())
        names_dict["_pth_kwargs"] = kwargs
        source_to_exec = self.fn_source_code
        source_to_exec += f"\n_pth_result = {self.fn_name}(**_pth_kwargs)\n"
        exec(source_to_exec, names_dict, names_dict)
        result = names_dict["_pth_result"]
        return result


    @property
    def decorator(self):
        return "@pth.ordinary()"