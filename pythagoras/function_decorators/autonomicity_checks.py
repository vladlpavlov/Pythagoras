from typing import Callable

from pythagoras.function_decorators.autonomous_funcs import (
    AutonomousFunction, LooselyAutonomousFunction, StrictlyAutonomousFunction)

def is_autonomous(a_func: Callable) -> bool:
    """Check if a function is autonomous."""
    assert callable(a_func)
    return isinstance(a_func, AutonomousFunction)


def is_loosely_autonomous(a_func: Callable) -> bool:
    """Check if a function is loosely autonomous.

    """
    assert callable(a_func)
    return isinstance(a_func, LooselyAutonomousFunction)


def is_strictly_autonomous(a_func: Callable) -> bool:
    """Check if a function is strictly autonomous."""
    assert callable(a_func)
    return isinstance(a_func, StrictlyAutonomousFunction)
