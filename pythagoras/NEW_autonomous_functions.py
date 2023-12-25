"""Work with autonomous functions.

Autonomous functions are only allowed to use the built-in objects
(functions, types, variables), as well as global objects,
accessible via import statements inside the function body.

Autonomous functions are not allowed to use free variables
(non-global/non-local objects). They are also not allowed to use
global objects, imported outside the function body.
"""
import ast
import inspect
from functools import wraps
from typing import Callable
from pythagoras.NEW_utils import get_normalized_function_source
import builtins


class FunctionDependencyAnalyzer(ast.NodeVisitor):
    """Collect data needed to analyze function autonomy.

    This class is a visitor of an AST (Abstract Syntax Tree) that collects data
    needed to analyze function autonomy.

    Attributes:
        all_outside_names: A set to store all the outside names
            found in the function.
        imported_global_names: A set to store the all object names,
            that are explicitly imported inside the function.
        imported_packages: A set to store the names of the packages,
            imported inside the function.
        nonimported_outside_names: A set to store the names of
            the global objects that are used in the function,
            but not explicitly imported inside it.
        nonlocal_names: A set to store the nonlocal names found in the function.
        local_names: A set to store the names of local variables,
            found in the function.
    """

    # TODO: add support for nested functions
    def __init__(self):
        self.imported_packages = set()
        self.imported_global_names = set()
        self.nonimported_outside_names = set()
        self.all_outside_names = set()
        self.local_names = set()
        self.nonlocal_names = set()

    def visit_FunctionDef(self, node):
        for arg in node.args.args:
            self.local_names |= {arg.arg}
        if node.args.vararg:
            self.local_names |= {node.args.vararg.arg}
        if node.args.kwarg:
            self.local_names |= {node.args.kwarg.arg}
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id not in self.local_names:
            self.all_outside_names |= {node.id}
            if node.id not in self.imported_global_names:
                self.nonimported_outside_names |= {node.id}
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id not in self.all_outside_names:
                    self.local_names |= {target.id}
        self.generic_visit(node)

    def visit_comprehension(self, node):
        target_id = node.target.id
        self.local_names |= {target_id}
        self.all_outside_names -= {target_id}
        self.nonimported_outside_names -= {target_id}
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_global_names |= {name}
            self.imported_packages |= {alias.name.split('.')[0]}
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module
        self.imported_packages |= {node.module.split('.')[-1]}
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_global_names |= {name}
        self.generic_visit(node)

    def visit_Nonlocal(self, node):
        for name in node.names:
            self.nonlocal_names |= {name}
        self.generic_visit(node)

    def visit_Global(self, node):
        for name in node.names:
            self.all_outside_names |= {name}
        self.generic_visit(node)

def analyze_function_dependencies(
        a_func: Callable
        ) -> FunctionDependencyAnalyzer:
    """Analyze function dependencies.

    It returns an instance of FunctionDependencyAnalyzer class,
    which contains all the data needed to analyze function autonomy.
    """
    assert callable(a_func), ("This acton can only"
        , " be applied to functions.")
    source = get_normalized_function_source(a_func)
    assert source.startswith("def "), ("This action can only"
        , " be applied to conventional functions,"
        , " not to instances of callable classes and"
        , " not to lambda functions.")
    tree = ast.parse(source)
    analyzer = FunctionDependencyAnalyzer()
    analyzer.visit(tree)
    return analyzer

class autonomous:
    """Decorator for autonomous functions.

    Autonomous functions are only allowed to use the built-in objects
    (functions, types, variables), as well as global objects,
    accessible via import statements inside the function body.
    """
    def __init__(self):
        pass

    def __call__(self, a_func: Callable) -> Callable:
        """Decorator for autonomous functions.

        It does both static and dynamic checks for autonomous functions.

        Static checks: it checks whether the function uses any non-global
        objects which do not have associated import statements
        inside the function. It also checks whether the function is using
        any free variables (non-global/non-local objects).
        If static checks fail, the decorator throws a NameError exception.

        Dynamic checks: during the execution time it hides all the global
        and non-local objects from the function, except the built-in ones.
        If a function tries to use a non-built-in object
        without importing it inside the function body,
        it will result in raising a NameError exception.
        """

        # Static checks

        analyzer = analyze_function_dependencies(a_func)

        builtin_names = set(dir(builtins))
        import_required = analyzer.nonimported_outside_names - builtin_names
        if import_required:
            raise NameError(f"The function {a_func.__name__}"
                , f" is not autonomous, it uses global"
                , f" objects {import_required}"
                , f" without importing them inside the function body")

        if len(a_func.__code__.co_freevars): #TODO: will ASTs serve better here?
            raise NameError(f"The function {a_func.__name__}"
                , f" is not autonomous, it uses non-global"
                , f" objects: {a_func.__code__.co_freevars}")

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

        return wrapper


def is_autonomous(a_func: Callable) -> bool:
    """Check if a function is autonomous."""
    assert callable(a_func)
    try:
        return a_func.__autonomous__
    except AttributeError:
        return False
