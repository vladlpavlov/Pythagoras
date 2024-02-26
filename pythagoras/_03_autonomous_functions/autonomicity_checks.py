from typing import Callable

from pythagoras._03_autonomous_functions.autonomous_funcs import (
    AutonomousFunction)

def is_autonomous(a_func: Callable) -> bool:
    """Check if a function is autonomous."""
    assert callable(a_func)
    return isinstance(a_func, AutonomousFunction)


def is_loosely_autonomous(a_func: Callable) -> bool:
    """Check if a function is loosely autonomous.

    """
    assert callable(a_func)
    return (isinstance(a_func, AutonomousFunction)
            and a_func.island_name is not None)


def is_strictly_autonomous(a_func: Callable) -> bool:
    """Check if a function is strictly autonomous."""
    assert callable(a_func)
    return (isinstance(a_func, AutonomousFunction)
            and a_func.island_name is None)
