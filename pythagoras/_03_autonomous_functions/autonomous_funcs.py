import builtins
from typing import Callable

from pythagoras._05_mission_control.global_state_management import get_all_cloudized_function_names
from pythagoras.python_utils.names_usage_analyzer import analyze_names_in_function
from pythagoras._01_foundational_objects.basic_exceptions import PythagorasException
import pythagoras as pth

class StaticAutonomicityChecksFailed(PythagorasException):
    pass

from pythagoras._02_ordinary_functions import get_normalized_function_source


class AutonomousFunction:

    def __init__(self, function:Callable,**_):
        self.function = function
        self.function_name = None
        self.function_source = None
        self.checks_passed = None

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()

    def check_autonomous_requirements(self, island_name = None)-> None:
        """
        Checks if a function meets the requirements to be an autonomous function.
        """
        if self.checks_passed is not None:
            assert isinstance(self.checks_passed, bool)
            return

        if hasattr(self.function, "__name__"):
            self.function_name = self.function.__name__

        if isinstance(self.function, AutonomousFunction):
            raise StaticAutonomicityChecksFailed(
                f"Function {self.function_name} "
                + f"is already autonomous, it can't be made autonomous twice.")

        analyzer = analyze_names_in_function(self.function)
        normalized_source = analyzer["normalized_source"]
        analyzer = analyzer["analyzer"]

        analyzer.names.explicitly_nonlocal_unbound_deep -= {
            "autonomous", "loosely_autonomous", "strictly_autonomous"}
        if len(analyzer.names.explicitly_nonlocal_unbound_deep):
            raise StaticAutonomicityChecksFailed(f"Function {self.function_name}"
                + f" is not autonomous, it uses external nonlocal"
                + f" objects: {analyzer.names.explicitly_nonlocal_unbound_deep}")

        builtin_names = set(dir(builtins))
        import_required = analyzer.names.explicitly_global_unbound_deep
        import_required |= analyzer.names.unclassified_deep
        import_required -= {"autonomous", "loosely_autonomous",
                            "strictly_autonomous"}
        import_required -= builtin_names
        if island_name is not None:
            import_required -= set(get_all_cloudized_function_names(island_name))
        if import_required:
            raise StaticAutonomicityChecksFailed(f"Function {self.function_name}"
                + f" is not autonomous, it uses global"
                + f" objects {import_required}"
                + f" without importing them inside the function body")

        if analyzer.n_yelds:
            raise StaticAutonomicityChecksFailed(f"Function {self.function_name}"
                + f" is not autonomous, it uses yield statements")

        if len(self.function.__code__.co_freevars):  # TODO: will ASTs serve better here?
            raise StaticAutonomicityChecksFailed(f"Function {self.function_name}"
                + f" is not autonomous, it uses non-global"
                + f" objects: {self.function.__code__.co_freevars}")

        self.function_source = normalized_source

        self.checks_passed = True


class StrictlyAutonomousFunction(AutonomousFunction):
    def __init__(self, function: Callable):
        super().__init__(function)
        self.check_autonomous_requirements()


    def __call__(self, *args, **kwargs):
        old_globals = {}
        global_names = list(self.function.__globals__.keys())

        # Dynamic checks TODO: find better way to do it
        for obj_name in global_names:
            if not (obj_name.startswith("__") or obj_name.startswith("@")):
                old_globals[obj_name] = self.function.__globals__[obj_name]
                del self.function.__globals__[obj_name]
        try:
            result = self.function(*args, **kwargs)
            return result
        except:
            self.checks_passed = False
            raise
        finally:
            for obj_name in old_globals:
                self.function.__globals__[obj_name] = old_globals[obj_name]
        return self.function(*args, **kwargs)

class LooselyAutonomousFunction(AutonomousFunction):
    def __init__(self, function: Callable, island_name:str=None):
        super().__init__(function)
        if island_name is None:
            island_name = pth.default_island_name
        self.island_name = island_name
        self.function_name = function.__name__
        self.function_source = get_normalized_function_source(function)


    def __call__(self, *args, **kwargs):
        old_globals = {}
        global_names = list(self.function.__globals__.keys())
        self.check_autonomous_requirements(island_name=self.island_name)

        # Dynamic checks TODO: find better way to do it
        for obj_name in global_names:
            if not (obj_name.startswith("__") or obj_name.startswith("@")):
                old_globals[obj_name] = self.function.__globals__[obj_name]
                del self.function.__globals__[obj_name]
        try:
            result = self.function(*args, **kwargs)
            return result
        except:
            self.checks_passed = False
            raise
        finally:
            for obj_name in old_globals:
                self.function.__globals__[obj_name] = old_globals[obj_name]
        return self.function(*args, **kwargs)