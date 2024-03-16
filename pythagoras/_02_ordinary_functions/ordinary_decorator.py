from typing import Callable

from pythagoras._02_ordinary_functions.ordinary_funcs import OrdinaryFn

class ordinary:
    def __init__(self):
        pass
    def __call__(self,a_func:Callable)->OrdinaryFn:
        decorated_function = OrdinaryFn(a_func)
        return decorated_function