"""Support for work with autonomous functions.

In an essence, an autonomous function contains self-sufficient code
that does not depend on external imports or definitions.

Autonomous functions are always allowed to use the built-in objects
(functions, types, variables), as well as global objects,
explicitly imported inside the function body. An autonomous function
may be allowed to use other autonomous functions, which are created or imported
outside the autonomous function, provided that they belong to the same island.

Autonomous functions are not allowed to:
    * use global objects, imported or defined outside the function body
      (except built-in objects and, possibly,
      other autonomous functions from the same island);
    * use yield (yield from) statements;
    * use nonlocal variables, referencing the outside objects.

If an autonomous function is allowed to use other autonomous functions,
it is called "loosely autonomous function". Otherwise, it is called
"strictly autonomous function".

Autonomous functions can have nested functions and classes.

Only ordinary functions can be autonomous. Asynchronous functions,
class methods and lambda functions cannot be autonomous.

Decorators @autonomous, @loosely_autonomous, and @strictly_autonomous
allow to inform Pythagoras that a function is intended to be autonomous,
and to enforce autonomicity requirements for the function.
"""
from typing import Callable

from pythagoras._010_basic_portals import PortalAwareClass
from pythagoras._060_autonomous_functions.autonomous_core_classes import (
    AutonomousFn, AutonomousCodePortal)



class autonomous(PortalAwareClass):
    """Decorator for enforcing autonomicity requirements for functions.

    A strictly autonomous function is only allowed to use the built-in objects
    (functions, types, variables), as well as global objects,
    accessible via import statements inside the function body.

    A loosely autonomous function is additionally allowed to
    use other autonomous functions, which are created or imported
    outside the autonomous function, provided that they belong to the same island.

    strictly_autonomous parameter indicates whether a function is a strictly
    or a loosely autonomous.
    """

    island_name: str | None

    def __init__(self, island_name: str | None = None
                 , strictly_autonomous: bool = False,
                 portal: AutonomousCodePortal | None = None):
        assert isinstance(island_name, str) or island_name is None
        self.island_name = island_name
        self.strictly_autonomous = strictly_autonomous
        super().__init__(portal=portal)

    @property
    def portal(self) -> AutonomousCodePortal:
        return super().portal

    def __call__(self, a_func: Callable|str) -> AutonomousFn:
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
        with self.portal:
            wrapper = AutonomousFn(
                a_func, island_name=self.island_name
                , strictly_autonomous=self.strictly_autonomous,
                portal=self.portal)
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
    def __init__(self
                 , island_name: str | None = None
                 , portal: AutonomousCodePortal | None = None):
        super().__init__(
            island_name=island_name
            , strictly_autonomous=True
            , portal=portal)