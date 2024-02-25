from __future__ import annotations
import builtins
from typing import Callable, Optional, Any
import pythagoras as pth

from pythagoras._02_ordinary_functions.ordinary_funcs import (
    OrdinaryFunction)

from pythagoras._03_autonomous_functions.default_island_singleton import (
    DefaultIslandType, DefaultIsland)

from pythagoras._99_misc_utils.decorator_names import get_all_decorator_names

from pythagoras.python_utils.names_usage_analyzer import (
    analyze_names_in_function)


class AutonomousFunction(OrdinaryFunction):
    # naked_source_code: str
    # name: str
    island_name:Optional[str]
    # default_island_name: str = "Samos"
    # all_autonomous_functions: dict[str, dict[str,AutonomousFunction]] = dict()

    def __init__(self, a_func: Callable | str | OrdinaryFunction
                 , island_name:str | None | DefaultIslandType = DefaultIsland):
        super().__init__(a_func)

        if island_name is DefaultIsland:
            island_name = pth.default_island_name

        if isinstance(a_func, AutonomousFunction):
            assert island_name == a_func.island_name

        if island_name is not None:
            assert isinstance(island_name, str)
            # TODO: Add checks for island_name (should be a safe str)

        if island_name not in pth.all_autonomous_functions:
            pth.all_autonomous_functions[island_name] = dict()

        island = pth.all_autonomous_functions[island_name]
        if self.name in island:
            existing_func = island[self.name]
            assert existing_func.naked_source_code == self.naked_source_code, (
                f"Function {self.name} is already "
                + "defined in island {island_name}"
                + f" with different source code. You cannot redefine it within"
                + f" one session of the program.")
            a_func = existing_func
        else:
            self._static_checks_passed = None
            self._runtime_checks_passed = None

        self.island_name = island_name

        if self.name not in island:
            island[self.name] = self

        assert self.static_autonomicity_checks()
        if self.island_name is None:
            assert self.runtime_autonomicity_checks()

        assert island_name in pth.all_autonomous_functions
        assert self.name in pth.all_autonomous_functions[island_name]
        assert self.naked_source_code == (
            pth.all_autonomous_functions[island_name][self.name].naked_source_code)
        assert hasattr(pth.all_autonomous_functions[island_name][self.name]
                       ,"_static_checks_passed")
        assert hasattr(pth.all_autonomous_functions[island_name][self.name]
                       ,"_runtime_checks_passed")
        if self is not pth.all_autonomous_functions[island_name][self.name]:
            assert not hasattr(self,"_static_checks_passed")
            assert not hasattr(self,"_runtime_checks_passed")



    @property
    def decorator(self) -> str:
        decorator_str =""
        if self.island_name is None:
            decorator_str = "@pth.strictly_autonomous()"
        else:
            decorator_str = f"@pth.autonomous(island_name={self.island_name})"
        return decorator_str

    def static_autonomicity_checks(self)-> bool:
        island = pth.all_autonomous_functions[self.island_name]
        name = self.name
        if island[name]._static_checks_passed is not None:
            assert isinstance(island[name]._static_checks_passed, bool)
            return island[name]._static_checks_passed

        analyzer = analyze_names_in_function(self.naked_source_code)
        normalized_source = analyzer["normalized_source"]
        analyzer = analyzer["analyzer"]
        assert self.naked_source_code == normalized_source


        nonlocal_names = analyzer.names.explicitly_nonlocal_unbound_deep
        nonlocal_names -= get_all_decorator_names()

        assert len(nonlocal_names) == 0, (f"Function {self.name}"
            + f" is not autonomous, it uses external nonlocal"
            + f" objects: {analyzer.names.explicitly_nonlocal_unbound_deep}")

        assert analyzer.n_yelds == 0, (f"Function {self.name}"
                + f" is not autonomous, it uses yield statements")

        self._static_checks_passed = True
        return True

    def runtime_autonomicity_checks(self)-> bool:
        island = pth.all_autonomous_functions[self.island_name]
        name = self.name

        if island[name]._runtime_checks_passed is not None:
            assert isinstance(island[name]._runtime_checks_passed, bool)
            return island[name]._runtime_checks_passed

        analyzer = analyze_names_in_function(self.naked_source_code)
        normalized_source = analyzer["normalized_source"]
        analyzer = analyzer["analyzer"]
        assert self.naked_source_code == normalized_source

        import_required = analyzer.names.explicitly_global_unbound_deep
        import_required |= analyzer.names.unclassified_deep
        import_required -= get_all_decorator_names()
        builtin_names = set(dir(builtins))
        import_required -= builtin_names
        if self.island_name is not None:
            island = pth.all_autonomous_functions[self.island_name]
            import_required -= set(island)

        assert len(import_required) ==0, (f"Function {self.name}"
            + f" is not autonomous, it uses global"
            + f" objects {import_required}"
            + f" without importing them inside the function body")

        self._runtime_checks_passed = True
        return True


    def __call__(self, **kwargs) -> Any:
        assert self.runtime_autonomicity_checks()
        names_dict = dict(globals())
        names_dict.update(locals())
        names_dict["__pth_kwargs"] = kwargs
        if self.island_name is not None:
            island = pth.all_autonomous_functions[self.island_name]
            names_dict.update(island)
        else:
            names_dict[self.name] = self

        tmp_name = "__pth_tmp_" + self.name
        source_to_exec = self.naked_source_code + "\n"
        source_to_exec = source_to_exec.replace(
            " "+self.name+"(", " "+tmp_name+"(",1)
        source_to_exec += f"\n__pth_result = {tmp_name}(**__pth_kwargs)\n"

        exec(source_to_exec, names_dict, names_dict)
        result = names_dict["__pth_result"]
        return result

    def __getstate__(self):
        draft_state = dict(name = self.name
            , naked_source_code = self.naked_source_code
            , island_name = self.island_name)
        state = dict()
        for key in sorted(draft_state):
            state[key] = draft_state[key]
        return state

    def __setstate__(self, state):
        assert len(state) == 3
        f = AutonomousFunction(state["naked_source_code"]
            , island_name=state["island_name"])
        assert f.name == state["name"]
        self.name = f.name
        self.naked_source_code = f.naked_source_code
        self.island_name = f.island_name



class StrictlyAutonomousFunction(AutonomousFunction):
    def __init__(self,a_func: Callable | str | OrdinaryFunction):
        super().__init__(a_func, island_name=None)
