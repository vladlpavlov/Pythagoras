from typing import Callable

from pythagoras._040_ordinary_functions.ordinary_funcs import OrdinaryFn

class ordinary:
    """A decorator that converts a Python function into an OrdinaryFn object.

    As a part of the conversion process, the source code of the function
    is checked. If it does not meet the requirements of an ordinary function,
    an exception is raised.
    """

    def __init__(self):
        pass
    def __call__(self,a_func:Callable)->OrdinaryFn:
        decorated_function = OrdinaryFn(a_func)
        return decorated_function