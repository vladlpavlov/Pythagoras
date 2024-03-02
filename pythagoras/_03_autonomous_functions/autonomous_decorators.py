"""Support for work with autonomous functions.

In an essence, an autonomous function contains self-sufficient code
that does not depend on external imports or definitions.

Autonomous functions are always allowed to use the built-in objects
(functions, types, variables), as well as global objects,
explicitly imported inside the function body. An autonomous function
may be allowed to use idempotent functions, which are created or imported
outside the autonomous function.

Autonomous functions are not allowed to:
    * use global objects, imported or defined outside the function body
      (except built-in objects and, possibly, idempotent functions);
    * use yield (yield from) statements;
    * use nonlocal variables, referencing the outside objects.

If an autonomous function is allowed to use outside idempotent functions,
it is called "loosely autonomous function". Otherwise, it is called
"strictly autonomous function".

Autonomous functions can have nested functions and classes.

Only conventional functions can be autonomous. Asynchronous functions,
class methods and lambda functions cannot be autonomous.

Decorators @autonomous, @loosely_autonomous, and @strictly_autonomous
allow to inform Pythagoras that a function is intended to be autonomous,
and to enforce autonomicity requirements for the function.
"""
from typing import Callable
import logging

from pythagoras._03_autonomous_functions.default_island_singleton import (
    DefaultIslandType, DefaultIsland)
from pythagoras._03_autonomous_functions.autonomous_funcs import (
     AutonomousFunction)
from pythagoras._05_mission_control.global_state_management import (
    is_fully_unitialized)


class autonomous:
    """Decorator for enforcing autonomicity requirements for functions.

    A strictly autonomous function is only allowed to use the built-in objects
    (functions, types, variables), as well as global objects,
    accessible via import statements inside the function body.

    A loosely autonomous function is additionally allowed to
    use idempotent functions, which are created or imported
    outside the autonomous function.

    allow_idempotent parameter indicates whether a function is a strictly
    or a loosely autonomous.
    """

    island_name: str | None
    require_pth: bool

    def __init__(self
            , island_name: str | None | DefaultIslandType = DefaultIsland
            , require_pth : bool = True):
        assert (isinstance(island_name, str)
                or island_name is None
                or island_name is DefaultIsland)
        self.island_name = island_name
        self.require_pth = require_pth

    def __call__(self, a_func: Callable) -> Callable:
        """Decorator for autonomous functions.

        It does both static and dynamic checks for autonomous functions.

        Static checks: it checks whether the function uses any global
        non-built-in objects which do not have associated import statements
        inside the function. If allow_idempotent==True,
        global idempotent functions are also allowed.
        The decorator also checks whether the function is using
        any non-local objects variables, and whether the function
        has yield / yield from statements in its code. If static checks fail,
        the decorator throws a FunctionAutonomicityError exception.

        Dynamic checks: during the execution time it hides all the global
        and non-local objects from the function, except the built-in ones
        (and idempotent ones, if allow_idempotent==True).
        If a function tries to use a non-built-in
        (and non-idempotent, if allow_idempotent==True)
        object without explicitly importing it inside the function body,
        it will result in raising an exception.

        Currently, neither static nor dynamic checks are guaranteed to catch
        all possible violations of function autonomy requirements.
        """
        if not self.require_pth and is_fully_unitialized():
            wrapper = a_func
            logging.warning(f"Decorator @{self.__class__.__name__}()"
            + f" is used with function {a_func.__name__}"
            + " before Pythagoras is initialized."
            + " Pythagoras functionality is disabled for this function.")
        else:
            wrapper = AutonomousFunction(a_func, self.island_name)
        return wrapper

class strictly_autonomous(autonomous):
    """Decorator for enforcing strict autonomicity requirements for functions.

    It does both static and dynamic checks for strictly autonomous functions.

    Static checks: it checks whether the function uses any global
    non-built-in objects which do not have associated import statements
    inside the function. It also checks whether the function is using
    any non-local objects variables, and whether the function
    has yield / yield from statements in its code. If static checks fail,
    the decorator throws a FunctionAutonomicityError exception.

    Dynamic checks: during the execution time it hides all the global
    and non-local objects from the function, except the built-in ones.
    If a function tries to use a non-built-in object
    without explicitly importing it inside the function body,
    it will result in raising an exception.

    Currently, neither static nor dynamic checks are guaranteed to catch
    all possible violations of strict function autonomicity requirements.
    """
    def __init__(self, require_pth: bool = True):
        super().__init__(island_name=None, require_pth=require_pth)
