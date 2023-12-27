from typing import Callable


def is_autonomous(a_func: Callable) -> bool:
    """Check if a function is autonomous."""
    assert callable(a_func)
    try:
        return a_func.__autonomous__
    except AttributeError:
        return False


def is_loosely_autonomous(a_func: Callable) -> bool:
    """Check if a function is loosely autonomous.

    """
    assert callable(a_func)
    try:
        return a_func.__autonomous__ and a_func.__loosely_autonomous__
    except AttributeError:
        return False

def is_strictly_autonomous(a_func: Callable) -> bool:
    """Check if a function is strictly autonomous."""
    assert callable(a_func)
    try:
        return a_func.__autonomous__ and a_func.__strictly_autonomous__
    except AttributeError:
        return False
