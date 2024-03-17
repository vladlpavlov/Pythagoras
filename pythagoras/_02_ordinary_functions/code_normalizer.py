from typing import Callable

from pythagoras._02_ordinary_functions.code_normalizer_implementation import (
    __get_normalized_function_source__)
from pythagoras._02_ordinary_functions.ordinary_funcs import OrdinaryFn

def get_normalized_function_source(a_func: OrdinaryFn | Callable | str) -> str:
    """Return function's source code in a 'canonical' form.

    Remove all comments, docstrings and empty lines;
    standardize code formatting based on PEP 8.

    Only regular functions are supported; methods and lambdas are not supported.
    """

    if isinstance(a_func, OrdinaryFn):
        return a_func.fn_source_code
    else:
        return __get_normalized_function_source__(a_func, drop_pth_decorators=True)