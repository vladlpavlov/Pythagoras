"""Work with autonomous functions.

An autonomous function is a function that does not use any variables / types / functions
that are imported outside the autonomous function, it has all the import statements inside the function body.
Autonomous functions are only allowed to use the built-in objects (functions, types, variables), and the objects,
accessible via import statements inside the function body.
"""

from functools import wraps
import builtins
from typing import Callable


def autonomous(a_func: Callable) -> Callable:
    """Decorator for autonomous functions.

    It hides from the function all the global and non-local objects,
    except the built-in ones. If a function tries to use a non-built-in object without
    importing it inside the function body, it will result in raising a NameError exception.
    """

    assert callable(a_func)

    if len(a_func.__code__.co_freevars):
        raise NameError(f"The function {a_func.__name__} is not autonomous, it uses "
                        , f"non-global/non-local objects {a_func.__code__.co_freevars}")

    @wraps(a_func)
    def wrapper(*args, **kwargs):

        old_globals = {}
        global_names = list(a_func.__globals__.keys())

        for obj_name in global_names:
            if not (obj_name.startswith("__") or obj_name.startswith("@")):
                old_globals[obj_name] = a_func.__globals__[obj_name]
                del a_func.__globals__[obj_name]
        try:
            result = a_func(*args, **kwargs)
            return result
        except:
            wrapper.__autonomous__ = False
            raise
        finally:
            for obj_name in old_globals:
                a_func.__globals__[obj_name] = old_globals[obj_name]

    wrapper.__autonomous__ = True

    return wrapper


def is_autonomous(a_func: Callable) -> bool:
    """Check if a function is autonomous."""
    assert callable(a_func)
    try:
        return a_func.__autonomous__
    except AttributeError:
        return False
