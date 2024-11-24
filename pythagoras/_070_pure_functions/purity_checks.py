from pythagoras._070_pure_functions.pure_core_classes import (
    PureFn)


def is_pure(a_func):
    assert callable(a_func)
    return isinstance(a_func, PureFn)