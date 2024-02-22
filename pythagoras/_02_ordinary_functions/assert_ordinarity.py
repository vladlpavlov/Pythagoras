import types
from typing import Callable
import inspect

import pythagoras as pth


def assert_ordinarity(a_func:Callable) -> None:
    """Assert that a function is ordinary.

    A function is ordinary if it is not a method,
    a classmethod, a staticmethod, or a lambda function,
    or a build-in function.

    Parameters:
    a_func (Callable): The function to be checked.

    Raises:
    AssertionError: If the function is not ordinary.
    """

    # TODO: decide how to handle static methods
    # currently they are treated as ordinary functions

    name = pth.get_long_infoname(a_func)

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