import types, inspect
from typing import Callable


from pythagoras._040_ordinary_functions.check_n_positional_args import (
    accepts_unlimited_positional_args)
from pythagoras._040_ordinary_functions.long_infoname import get_long_infoname


def assert_ordinarity(a_func:Callable) -> None:
    """Assert that a function is ordinary.

    A function is ordinary if it is not a method,
    a classmethod, a staticmethod, or a lambda function,
    or a build-in function.

    assert_ordinarity check a function, given as an input parameter,
    and throws an exception the function is not ordinary.
    """

    # TODO: decide how to handle static methods
    # currently they are treated as ordinary functions

    name = get_long_infoname(a_func)

    assert callable(a_func), f"{name} must be callable."

    assert inspect.isfunction(a_func), (
        f"The function {name} is not ordinary."
        " It must be a function, not a method, "
        "a classmethod, or a lambda function."
        )

    assert not isinstance(a_func, types.MethodType), (
            f"The function {name} can't be an instance or a class method,"
            " only regular functions are allowed"
            )

    assert not (hasattr(a_func, "__closure__")
                and a_func.__closure__ is not None), (
        f"The function {name} can't be a closure,"
        " only regular functions are allowed."
        )

    assert a_func.__name__ != "<lambda>", (
        f"The function {name} can't be lambda,"
        " only regular functions are allowed."
        )

    assert not accepts_unlimited_positional_args(a_func), (
        "Pythagoras only allows functions with named arguments."
        f" But {name} accepts unlimited (nameless) positional arguments."
        )

    assert not inspect.iscoroutinefunction(a_func), (
        f"The function {name} can't be an async function,"
        " only regular functions are allowed."
        )