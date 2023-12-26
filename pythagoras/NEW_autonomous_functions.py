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
from copy import deepcopy
from functools import wraps
from typing import Callable, Set
from pythagoras.NEW_utils import get_normalized_function_source
import builtins


class NamesUsedInFunction:
    def __init__(self):
        self.explicitly_global_unbound_deep = set() # names, explicitly marked as global inside the function and/or called subfunctions, yet not bound to any object
        self.explicitly_nonlocal_unbound_deep = set() # names, explicitly marked as nonlocal inside the function and/or called subfunctions, yet not bound to any object
        self.local = set() # local variables in a function
        self.imported = set() # all names, which are explixitly imported inside the function
        self.unclassified_deep = set() # names, used inside the function and/or called subfunctions, while not explicitly imported, amd not explicitly marked as nonlocal / global
        self.accessible = set() # all names, currently accessable within the function

class FunctionDependencyAnalyzer(ast.NodeVisitor):
    """Collect data needed to analyze function autonomy.

    This class is a visitor of an AST (Abstract Syntax Tree) that collects data
    needed to analyze function autonomy.
    """

    def __init__(self):
        self.names = NamesUsedInFunction()
        self.imported_packages_deep = set()
        self.func_nesting_level = 0

    def visit_FunctionDef(self, node):
        if self.func_nesting_level == 0:
            self.func_nesting_level += 1
            for arg in node.args.args:
                self.names.accessible |= {arg.arg}
                self.names.local |= {arg.arg}
            if node.args.vararg:
                self.names.local |= {node.args.vararg.arg}
            if node.args.kwarg:
                self.names.local |= {node.args.kwarg.arg}
            self.names.accessible |= self.names.local
            self.generic_visit(node)
            self.func_nesting_level -= 1
        else: ###TBD
            nested = FunctionDependencyAnalyzer()
            nested.visit(node)
            self.imported_packages_deep |= nested.imported_packages_deep
            nested.names.explicitly_nonlocal_unbound_deep -= self.names.local
            self.names.explicitly_nonlocal_unbound_deep |= nested.names.explicitly_nonlocal_unbound_deep
            self.names.explicitly_global_unbound_deep |= nested.names.explicitly_global_unbound_deep
            nested.names.unclassified_deep -= self.names.local
            nested.names.unclassified_deep -= self.names.imported
            self.names.unclassified_deep |= nested.names.unclassified_deep
            self.names.local |= {node.name}
            self.names.accessible |= {node.name}
            # self.names.imported is not changing


    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id not in self.names.accessible:
                self.names.unclassified_deep |= {node.id}
                self.names.accessible |= {node.id}
        if isinstance(node.ctx, ast.Store):
            if node.id not in self.names.accessible:
                self.names.local |= {node.id}
                self.names.accessible |= {node.id}
        self.generic_visit(node)

    def visit_comprehension(self, node):
        if isinstance(node.target, (ast.Tuple, ast.List)):
            all_targets =node.target.elts
        else:
            all_targets = [node.target]
        for target in all_targets:
            if isinstance(target, ast.Name):
                if target.id not in self.names.accessible:
                    self.names.local |= {target.id}
                    self.names.accessible |= {target.id}
        self.generic_visit(node)


    def visit_For(self, node):
        self.visit_comprehension(node)

    def visit_ListComp(self, node):
        for gen in node.generators:
            self.visit_comprehension(gen)
        self.generic_visit(node)

    def visit_SetComp(self, node):
        for gen in node.generators:
            self.visit_comprehension(gen)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        for gen in node.generators:
            self.visit_comprehension(gen)
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        for gen in node.generators:
            self.visit_comprehension(gen)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.names.imported |= {name}
            self.names.accessible |= {name}
            self.names.local |= {name}
            self.imported_packages_deep |= {alias.name.split('.')[0]}
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.imported_packages_deep |= {node.module.split('.')[-1]}
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.names.imported |= {name}
            self.names.accessible |= {name}
            self.names.local |= {name}
        self.generic_visit(node)

    def visit_Nonlocal(self, node):
        self.names.explicitly_nonlocal_unbound_deep |= set(node.names)
        self.names.accessible |= set(node.names)
        self.generic_visit(node)

    def visit_Global(self, node):
        self.names.explicitly_global_unbound_deep |= set(node.names)
        self.names.accessible |= set(node.names)
        self.generic_visit(node)

def analyze_function_dependencies(
        a_func: Callable
        ):
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
    result = dict(tree=tree, analyzer=analyzer)
    return result

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

        Static checks: it checks whether the function uses any global
        non-built-in objects which do not have associated import statements
        inside the function. It also checks whether the function is using
        any free variables (non-global/non-local objects).
        If static checks fail, the decorator throws a NameError exception.

        Dynamic checks: during the execution time it hides all the global
        and non-local objects from the function, except the built-in ones.
        If a function tries to use a non-built-in object
        without explicitly importing it inside the function body,
        it will result in raising a NameError exception.

        Currently, neither static nor dynamic checks are guaranteed to catch
        all possible violations of function autonomy requirements.
        """

        # Static checks

        analyzer = analyze_function_dependencies(a_func)["analyzer"]

        if len(analyzer.names.explicitly_nonlocal_unbound_deep):
            raise NameError(f"The function {a_func.__name__}"
                , f" is not autonomous, it uses external nonlocal"
                , f" objects: {analyzer.names.explicitly_nonlocal_unbound_deep}")

        builtin_names = set(dir(builtins))
        import_required = analyzer.names.explicitly_global_unbound_deep
        import_required |= analyzer.names.unclassified_deep
        import_required -= builtin_names
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