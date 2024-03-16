"""Decorators and utilities to work with autonomous functions.

In an essence, an autonomous function contains self-sufficient code
that does not depend on external imports or definitions.

Autonomous functions are always allowed to use the built-in objects
(functions, types, variables), as well as global objects,
explicitly imported inside the function body. An autonomous function
may be allowed to use some other autonomous functions,
created or imported outside the autonomous function.

Autonomous functions are not allowed to:

    * use global objects, imported or defined outside the function body
      (except built-in objects and, possibly, some other autonomous functions);
    * use yield (yield from) statements;
    * use nonlocal variables, referencing the outside objects.

If an autonomous function is allowed to use other autonomous functions,
it is called "loosely autonomous function". Otherwise, it is called
"strictly autonomous function".

Autonomous functions can have nested functions and classes.

Only regular functions can be autonomous. Asynchronous functions,
class methods and lambda functions cannot be autonomous.

This module defines  decorators which are used to
inform Pythagoras that a function is intended to be autonomous,
and to enforce autonomicity requirements:
@autonomous and @strictly_autonomous.

It also defines functions which are used to check whether a corresponding
decorator was added earlier to another function: is_autonomous(),
is_loosely_autonomous(), and is_strictly_autonomous().

Applying a decorator to a function ensures both static and runtime autonomicity
checks are performed for the function. Static checks happen at the time
of decoration, while dynamic checks happen at the time of function call.
"""


from pythagoras._03_autonomous_functions.autonomous_funcs import (
    AutonomousFn)

from pythagoras._03_autonomous_functions.autonomicity_checks import (
    is_autonomous, is_loosely_autonomous)

# from pythagoras._03_autonomous_functions.autonomicity_checks import (
#     is_strictly_autonomous)

from pythagoras._03_autonomous_functions.autonomous_decorators import (
    autonomous, strictly_autonomous)