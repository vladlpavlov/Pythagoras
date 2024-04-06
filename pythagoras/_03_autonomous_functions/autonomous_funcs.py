from __future__ import annotations
import builtins
from typing import Callable, Any


from pythagoras._01_foundational_objects.hash_and_random_signatures import (
    get_random_signature)

from pythagoras._02_ordinary_functions.ordinary_funcs import (
    OrdinaryFn)

from pythagoras._03_autonomous_functions.call_graph_explorer import (
    explore_call_graph_deep)

from pythagoras._03_autonomous_functions.names_usage_analyzer import (
    analyze_names_in_function)

from pythagoras._03_autonomous_functions.pth_available_names_retriever import (
    retrieve_objs_available_inside_autonomous_functions)

from pythagoras._05_events_and_exceptions.global_event_loggers import (
    register_exception_globally)

import pythagoras as pth


class AutonomousFn(OrdinaryFn):
    island_name:str
    strictly_autonomous:bool

    def __init__(self, a_fn: Callable | str | OrdinaryFn
                 , island_name:str | None = None
                 , strictly_autonomous:bool = False):

        super().__init__(a_fn)

        if island_name is None:
            island_name = pth.default_island_name
        assert isinstance(island_name, str)
        # TODO: Add checks for island_name (should be a safe str)

        if isinstance(a_fn, AutonomousFn):
            assert island_name == a_fn.island_name

        self.island_name = island_name

        self.strictly_autonomous = bool(strictly_autonomous)

        if self.__class__.__name__ == AutonomousFn.__name__:
            register_autonomous_function(self)


    @property
    def fn_type(self) -> str:
        if self.strictly_autonomous:
            return "strictly_autonomous"
        else:
            return "autonomous"

    @property
    def decorator(self) -> str:
        decorator_str ="@pth."+self.fn_type
        decorator_str += f"(island_name='{self.island_name}')"
        return decorator_str

    @property
    def dependencies(self) -> list[str]:
        island = pth.all_autonomous_functions[self.island_name]
        name = self.fn_name
        assert island[name]._dependencies is not None
        assert isinstance(island[name]._dependencies,list)
        assert len(island[name]._dependencies) >= 1
        return sorted(island[name]._dependencies)

    def perform_static_checks(self)-> bool:
        island = pth.all_autonomous_functions[self.island_name]
        name = self.fn_name
        if island[name]._static_checks_passed is not None:
            assert isinstance(island[name]._static_checks_passed, bool)
            return island[name]._static_checks_passed

        analyzer = analyze_names_in_function(self.fn_source_code)
        normalized_source = analyzer["normalized_source"]
        analyzer = analyzer["analyzer"]
        assert self.fn_source_code == normalized_source


        nonlocal_names = analyzer.names.explicitly_nonlocal_unbound_deep
        nonlocal_names -= set(pth.all_decorators)

        assert len(nonlocal_names) == 0, (f"Function {self.fn_name}"
            + f" is not autonomous, it uses external nonlocal"
            + f" objects: {analyzer.names.explicitly_nonlocal_unbound_deep}")

        assert analyzer.n_yelds == 0, (f"Function {self.fn_name}"
                + f" is not autonomous, it uses yield statements")

        self._static_checks_passed = True
        return True

    def perform_runtime_checks(self)-> bool:
        island = pth.all_autonomous_functions[self.island_name]
        name = self.fn_name

        if island[name]._runtime_checks_passed is not None:
            assert isinstance(island[name]._runtime_checks_passed, bool)
            return island[name]._runtime_checks_passed

        analyzer = analyze_names_in_function(self.fn_source_code)
        normalized_source = analyzer["normalized_source"]
        analyzer = analyzer["analyzer"]
        assert self.fn_source_code == normalized_source

        import_required = analyzer.names.explicitly_global_unbound_deep
        import_required |= analyzer.names.unclassified_deep
        import_required -= set(pth.primary_decorators)
        builtin_names = set(dir(builtins))
        import_required -= builtin_names
        pth_names = set(retrieve_objs_available_inside_autonomous_functions())
        import_required -= pth_names
        import_required -= {name}
        if not self.strictly_autonomous:
            island = pth.all_autonomous_functions[self.island_name]
            import_required -= set(island)

        assert len(import_required) ==0, (f"Function {self.fn_name}"
            + f" is not autonomous, it uses global"
            + f" objects {import_required}"
            + f" without importing them inside the function body")

        all_functions_in_island = [f.fn_source_code for f in island.values()]
        deep_dependencies = explore_call_graph_deep(all_functions_in_island)
        dependencies = deep_dependencies[name]
        assert isinstance(dependencies, set)
        assert len(dependencies) >= 1
        island[name]._dependencies = sorted(dependencies)
        island[name]._runtime_checks_passed = True
        return True


    def execute(self, **kwargs) -> Any:
        try:
            assert self.perform_runtime_checks()
            names_dict = retrieve_objs_available_inside_autonomous_functions()
            island = pth.all_autonomous_functions[self.island_name]
            names_dict["_pth_kwargs"] = kwargs
            if self.island_name is not None:
                for f_name in self.dependencies:
                    names_dict[f_name] = island[f_name]
            else:
                names_dict[self.fn_name] = island[self.fn_name]


            tmp_name = "_pth_tmp_" + self.fn_name
            source_to_exec = self.fn_source_code + "\n"
            source_to_exec = source_to_exec.replace(
                " "+self.fn_name+"(", " "+tmp_name+"(",1)
            source_to_exec += f"\n_pth_result = {tmp_name}(**_pth_kwargs)\n"
            exec(source_to_exec, names_dict, names_dict)
            result = names_dict["_pth_result"]
            return result
        except Exception as e:
            if self.__class__ == AutonomousFn:
                exception_id = f"{self.fn_name}_{self.island_name}"
                exception_id += f"_{e.__class__.__name__}"
                exception_id += f"_{get_random_signature()}"
                register_exception_globally(exception_id=exception_id)
            raise e

    def __call__(self,* args, **kwargs) -> Any:
        assert len(args) == 0, (f"Function {self.fn_name} can't"
            + " be called with positional arguments,"
            + " only keyword arguments are allowed.")
        return self.execute(**kwargs)

    def __getstate__(self):
        draft_state = dict(fn_name = self.fn_name
            , fn_source_code = self.fn_source_code
            , island_name = self.island_name
            , strictly_autonomous = self.strictly_autonomous
            , class_name = self.__class__.__name__)
        state = dict()
        for key in sorted(draft_state):
            state[key] = draft_state[key]
        return state

    def __setstate__(self, state):
        assert len(state) == 5
        assert state["class_name"] == AutonomousFn.__name__
        self.fn_name = state["fn_name"]
        self.fn_source_code = state["fn_source_code"]
        self.island_name = state["island_name"]
        self.strictly_autonomous = state["strictly_autonomous"]
        register_autonomous_function(self)


def register_autonomous_function(a_fn: AutonomousFn) -> None:
    assert isinstance(a_fn, AutonomousFn)
    island_name = a_fn.island_name
    fn_name = a_fn.fn_name
    if island_name not in pth.all_autonomous_functions:
        pth.all_autonomous_functions[island_name] = dict()
    island = pth.all_autonomous_functions[island_name]
    if fn_name not in island:
        island[fn_name] = a_fn
        island[fn_name]._static_checks_passed = None
        island[fn_name]._runtime_checks_passed = None
        island[fn_name]._dependencies = None
    else:
        assert a_fn.fn_source_code == island[fn_name].fn_source_code, (
                f"Function {fn_name} is already "
                + f"defined in island {island_name}"
                + f" with different source code. You cannot change it within"
                + f" one session of the program.")
        assert a_fn.decorator == island[a_fn.fn_name].decorator, (
                f"Function {fn_name} is already "
                + f"defined in island {island_name} with the same source code "
                + f"but different decorator. You cannot change decorator "
                + f"within one session of the program.")
        assert type(a_fn) == type(island[a_fn.fn_name])

    assert a_fn.perform_static_checks()
    if a_fn.strictly_autonomous:
        assert a_fn.perform_runtime_checks()

    assert a_fn.island_name in pth.all_autonomous_functions
    assert a_fn.fn_name in pth.all_autonomous_functions[island_name]
    assert a_fn.fn_source_code == (
        pth.all_autonomous_functions[a_fn.island_name][a_fn.fn_name].fn_source_code)
    assert hasattr(pth.all_autonomous_functions[a_fn.island_name][a_fn.fn_name]
                   , "_static_checks_passed")
    assert hasattr(pth.all_autonomous_functions[a_fn.island_name][a_fn.fn_name]
                   , "_runtime_checks_passed")
    assert hasattr(pth.all_autonomous_functions[a_fn.island_name][a_fn.fn_name]
                   , "_dependencies")
    if a_fn is not pth.all_autonomous_functions[a_fn.island_name][a_fn.fn_name]:
        assert not hasattr(a_fn, "_static_checks_passed")
        assert not hasattr(a_fn, "_runtime_checks_passed")
        assert not hasattr(a_fn, "_dependencies")