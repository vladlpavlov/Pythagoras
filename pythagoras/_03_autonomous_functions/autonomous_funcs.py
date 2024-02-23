import builtins
from typing import Callable, Optional

from pythagoras._01_foundational_objects.basic_exceptions import (
    PythagorasException)

from pythagoras._02_ordinary_functions import (
    get_normalized_function_source, OrdinaryFunction)

from pythagoras._02_ordinary_functions.ordinary_funcs import (
    OrdinaryFunction)

from pythagoras._05_mission_control.global_state_management import (
    get_all_cloudized_function_names)

from pythagoras.python_utils.names_usage_analyzer import (
    analyze_names_in_function)

import pythagoras as pth


class StaticAutonomicityChecksFailed(PythagorasException):
    pass


class AutonomousFunction(OrdinaryFunction):

    island_name:Optional[str]
    checks_passed:Optional[bool]

    def __init__(self, a_func: Callable | str | OrdinaryFunction
                 , island_name:Optional[str]=None):

        super().__init__(a_func)
        if island_name is not None:
            assert island_name in pth.get_all_island_names()

        if isinstance(a_func, AutonomousFunction):
            assert island_name == a_func.island_name
            self.island_name = a_func.island_name
            self.checks_passed = a_func.checks_passed
        else:
            self.island_name = island_name
            self.checks_passed = None

        self.check_autonomous_requirements()

    def _call_naked_code(self, **kwargs):
        names_dict = dict(globals())
        names_dict.update(locals())
        names_dict["__pth_kwargs"] = kwargs
        if self.island_name is not None:
            assert not self.name in pth.get_island(self.island_name)
            names_dict.update(pth.get_island(self.island_name))
        source_to_exec = self.naked_source_code
        source_to_exec += f"\n__pth_result = {self.name}(**__pth_kwargs)\n"
        exec(source_to_exec, names_dict, names_dict)
        result = names_dict["__pth_result"]
        return result

    def check_autonomous_requirements(self)-> None:
        """
        Checks if a function meets the requirements to be an autonomous function.
        """
        if self.checks_passed is not None:
            assert isinstance(self.checks_passed, bool)
            return

        analyzer = analyze_names_in_function(self.naked_source_code)
        normalized_source = analyzer["normalized_source"]
        analyzer = analyzer["analyzer"]
        assert self.naked_source_code == normalized_source

        analyzer.names.explicitly_nonlocal_unbound_deep -= {
            "autonomous", "loosely_autonomous", "strictly_autonomous"}
        if len(analyzer.names.explicitly_nonlocal_unbound_deep):
            raise StaticAutonomicityChecksFailed(f"Function {self.name}"
                + f" is not autonomous, it uses external nonlocal"
                + f" objects: {analyzer.names.explicitly_nonlocal_unbound_deep}")

        builtin_names = set(dir(builtins))
        import_required = analyzer.names.explicitly_global_unbound_deep
        import_required |= analyzer.names.unclassified_deep
        import_required -= {"autonomous", "loosely_autonomous",
                            "strictly_autonomous"}
        import_required -= builtin_names
        if self.island_name is not None:
            import_required -= set(get_all_cloudized_function_names(self.island_name))
        if import_required:
            raise StaticAutonomicityChecksFailed(f"Function {self.name}"
                + f" is not autonomous, it uses global"
                + f" objects {import_required}"
                + f" without importing them inside the function body")

        if analyzer.n_yelds:
            raise StaticAutonomicityChecksFailed(f"Function {self.name}"
                + f" is not autonomous, it uses yield statements")

        self.checks_passed = True


class StrictlyAutonomousFunction(AutonomousFunction):
    def __init__(self,a_func: Callable | str | OrdinaryFunction):
        super().__init__(a_func, island_name=None)