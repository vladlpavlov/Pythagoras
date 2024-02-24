from typing import Callable

from pythagoras._02_ordinary_functions.ordinary_funcs import OrdinaryFunction

class ordinary:
    def __init__(self):
        pass
    def __call__(self,a_func:Callable)->OrdinaryFunction:
        decorated_function = OrdinaryFunction(a_func)
        return decorated_function