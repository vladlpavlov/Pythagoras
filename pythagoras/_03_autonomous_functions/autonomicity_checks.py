from typing import Callable

from pythagoras._03_autonomous_functions.autonomous_funcs import (
    AutonomousFunction)

def is_autonomous(a_func: Callable) -> bool:
    """Check if a function is autonomous."""
    assert callable(a_func)
    return isinstance(a_func, AutonomousFunction)


def is_loosely_autonomous(a_func: Callable) -> bool:
    """Check if a function is loosely autonomous.

    A loosely autonomous function is allowed to call other autonomous
    functions that belong to the same island.
    """
    assert callable(a_func)
    return (isinstance(a_func, AutonomousFunction)
            and not a_func.strictly_autonomous)


def is_strictly_autonomous(a_func: Callable) -> bool:
    """Check if a function is strictly autonomous.

    A strictly autonomous function is fully safe-contained.
    It is not allowed to call other autonomous functions.
    """
    assert callable(a_func)
    return (isinstance(a_func, AutonomousFunction)
            and a_func.strictly_autonomous)