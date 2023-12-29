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
from pythagoras._source_code_processing.function_dependency_analyzer import *
from pythagoras.autonomous.autonomicity_checks import *
from functools import wraps
import builtins

class StaticAutonomicityChecksFailed(PythagorasException):
    pass

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
    def __init__(self, allow_idempotent: bool = False):
        self.allow_idempotent = allow_idempotent
        pass

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

        # Static checks

        if is_autonomous(a_func):
            raise StaticAutonomicityChecksFailed(f"Function {a_func.__name__} "
                + f"is already autonomous, it can't be made autonomous twice.")

        analyzer = analyze_function_dependencies(a_func)["analyzer"]

        if len(analyzer.names.explicitly_nonlocal_unbound_deep):
            raise StaticAutonomicityChecksFailed(f"Function {a_func.__name__}"
                + f" is not autonomous, it uses external nonlocal"
                + f" objects: {analyzer.names.explicitly_nonlocal_unbound_deep}")

        builtin_names = set(dir(builtins))
        import_required = analyzer.names.explicitly_global_unbound_deep
        import_required |= analyzer.names.unclassified_deep
        import_required -= builtin_names
        if import_required:
            raise StaticAutonomicityChecksFailed(f"Function {a_func.__name__}"
                + f" is not autonomous, it uses global"
                + f" objects {import_required}"
                + f" without importing them inside the function body")

        if analyzer.n_yelds:
            raise StaticAutonomicityChecksFailed(f"Function {a_func.__name__}"
                + f" is not autonomous, it uses yield statements")

        if len(a_func.__code__.co_freevars): #TODO: will ASTs serve better here?
            raise StaticAutonomicityChecksFailed(f"Function {a_func.__name__}"
                + f" is not autonomous, it uses non-global"
                + f" objects: {a_func.__code__.co_freevars}")

        @wraps(a_func)
        def wrapper(*args, **kwargs):

            old_globals = {}
            global_names = list(a_func.__globals__.keys())

            # Dynamic checks
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

        if self.allow_idempotent:
            wrapper.__loosely_autonomous__ = True
        else:
            wrapper.__strictly_autonomous__ = True
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
    def __init__(self):
        super().__init__(allow_idempotent=False)

class loosely_autonomous(autonomous):
    """Decorator for enforcing loose autonomicity requirements for functions.

    It does both static and dynamic checks for loosely autonomous functions.

    Static checks: it checks whether the function uses any global
    non-built-in / non-idempotent objects which do not have associated
    import statements inside the function. It also checks whether the function
    is using any non-local objects variables, and whether the function
    has yield / yield from statements in its code. If static checks fail,
    the decorator throws a FunctionAutonomicityError exception.

    Dynamic checks: during the execution time it hides all the global
    and non-local objects from the function,
    except the built-in and idempotent ones.
    If a function tries to use a non-built-in/non-idempotent object
    without explicitly importing it inside the function body,
    it will result in raising an exception.

    Currently, neither static nor dynamic checks are guaranteed to catch
    all possible violations of loose function autonomicity requirements.
    """
    def __init__(self):
        super().__init__(allow_idempotent=True)