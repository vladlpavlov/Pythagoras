from __future__ import annotations
import builtins
from typing import Callable, Optional, Any
import pythagoras as pth

from pythagoras._02_ordinary_functions.ordinary_funcs import (
    OrdinaryFunction)

from pythagoras._03_autonomous_functions.default_island_singleton import (
    DefaultIslandType, DefaultIsland)

from pythagoras._03_autonomous_functions.call_graph_explorer import (
    explore_call_graph_deep)

from pythagoras._03_autonomous_functions.names_usage_analyzer import (
    analyze_names_in_function)

from pythagoras._05_mission_control.global_state_management import (
    is_correctly_initialized)


class AutonomousFunction(OrdinaryFunction):
    # naked_source_code: str
    # name: str
    island_name:Optional[str]


    def __init__(self, a_func: Callable | str | OrdinaryFunction
                 , island_name:str | None | DefaultIslandType = DefaultIsland):
        assert is_correctly_initialized()
        super().__init__(a_func)

        if island_name is DefaultIsland:
            island_name = pth.default_island_name

        if isinstance(a_func, AutonomousFunction):
            assert island_name == a_func.island_name

        if island_name is not None:
            assert isinstance(island_name, str)
            # TODO: Add checks for island_name (should be a safe str)

        self.island_name = island_name

        if self.__class__.__name__ == AutonomousFunction.__name__:
            register_autonomous_function(self)



    @property
    def decorator(self) -> str:
        decorator_str =""
        if self.island_name is None:
            decorator_str = "@pth.strictly_autonomous()"
        else:
            decorator_str = f"@pth.autonomous(island_name={self.island_name})"
        return decorator_str

    @property
    def dependencies(self) -> list[str]:
        island = pth.all_autonomous_functions[self.island_name]
        name = self.name
        assert island[name]._dependencies is not None
        assert isinstance(island[name]._dependencies,list)
        assert len(island[name]._dependencies) >= 1
        return sorted(island[name]._dependencies)

    def static_checks(self)-> bool:
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
        nonlocal_names -= set(pth.all_decorators)

        assert len(nonlocal_names) == 0, (f"Function {self.name}"
            + f" is not autonomous, it uses external nonlocal"
            + f" objects: {analyzer.names.explicitly_nonlocal_unbound_deep}")

        assert analyzer.n_yelds == 0, (f"Function {self.name}"
                + f" is not autonomous, it uses yield statements")

        self._static_checks_passed = True
        return True

    def runtime_checks(self)-> bool:
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
        import_required -= set(pth.primary_decorators)
        builtin_names = set(dir(builtins))
        import_required -= builtin_names
        import_required -= {name}
        if self.island_name is not None:
            island = pth.all_autonomous_functions[self.island_name]
            import_required -= set(island)

        assert len(import_required) ==0, (f"Function {self.name}"
            + f" is not autonomous, it uses global"
            + f" objects {import_required}"
            + f" without importing them inside the function body")

        all_functions_in_island = [f.naked_source_code for f in island.values()]
        deep_dependencies = explore_call_graph_deep(all_functions_in_island)
        dependencies = deep_dependencies[name]
        assert isinstance(dependencies, set)
        assert len(dependencies) >= 1
        island[name]._dependencies = sorted(dependencies)
        island[name]._runtime_checks_passed = True
        return True


    def __call__(self, **kwargs) -> Any:
        assert self.runtime_checks()
        # names_dict = dict(globals())
        # names_dict.update(locals())
        names_dict = dict()
        island = pth.all_autonomous_functions[self.island_name]
        names_dict["__pth_kwargs"] = kwargs
        if self.island_name is not None:
            for f_name in self.dependencies:
                names_dict[f_name] = island[f_name]
        else:
            names_dict[self.name] = island[self.name]

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
            , island_name = self.island_name
            , class_name = self.__class__.__name__)
        state = dict()
        for key in sorted(draft_state):
            state[key] = draft_state[key]
        return state

    def __setstate__(self, state):
        assert len(state) == 4
        assert state["class_name"] == AutonomousFunction.__name__
        self.name = state["name"]
        self.naked_source_code = state["naked_source_code"]
        self.island_name = state["island_name"]
        register_autonomous_function(self)


def register_autonomous_function(f: AutonomousFunction) -> None:
    assert isinstance(f, AutonomousFunction)
    island_name = f.island_name
    name = f.name
    if island_name not in pth.all_autonomous_functions:
        pth.all_autonomous_functions[island_name] = dict()
    island = pth.all_autonomous_functions[island_name]
    if name not in island:
        island[name] = f
        island[name]._static_checks_passed = None
        island[name]._runtime_checks_passed = None
        island[name]._dependencies = None
    else:
        assert f.naked_source_code == island[name].naked_source_code, (
                f"Function {name} is already "
                + f"defined in island {island_name}"
                + f" with different source code. You cannot change it within"
                + f" one session of the program.")
        assert f.decorator == island[f.name].decorator, (
                f"Function {name} is already "
                + f"defined in island {island_name} with the same source code "
                + f"but different decorator. You cannot change decorator "
                + f"within one session of the program.")
        assert type(f) == type(island[f.name])

    assert f.static_checks()
    if f.island_name is None:
        assert f.runtime_checks()

    assert f.island_name in pth.all_autonomous_functions
    assert f.name in pth.all_autonomous_functions[island_name]
    assert f.naked_source_code == (
        pth.all_autonomous_functions[f.island_name][f.name].naked_source_code)
    assert hasattr(pth.all_autonomous_functions[f.island_name][f.name]
                   , "_static_checks_passed")
    assert hasattr(pth.all_autonomous_functions[f.island_name][f.name]
                   , "_runtime_checks_passed")
    assert hasattr(pth.all_autonomous_functions[f.island_name][f.name]
                   , "_dependencies")
    if f is not pth.all_autonomous_functions[f.island_name][f.name]:
        assert not hasattr(f, "_static_checks_passed")
        assert not hasattr(f, "_runtime_checks_passed")
        assert not hasattr(f, "_dependencies")
