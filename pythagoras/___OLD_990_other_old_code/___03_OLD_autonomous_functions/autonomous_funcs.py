from __future__ import annotations

import atexit
import builtins
from typing import Callable, Any
from persidict import PersiDict
from random import Random

import pythagoras._090_swarming_portals.clean_runtime_id
from pythagoras._010_basic_portals import PortalAwareClass
from pythagoras._800_persidict_extensions.overlapping_multi_dict import OverlappingMultiDict
from pythagoras._030_data_portals.data_portals import DataPortal
from pythagoras._820_strings_signatures_converters.random_signatures import (
    get_random_signature)

from pythagoras._040_ordinary_functions.ordinary_core_classes import (
    OrdinaryFn)

from pythagoras.___03_OLD_autonomous_functions.call_graph_explorer import (
    explore_call_graph_deep)

from pythagoras.___03_OLD_autonomous_functions.names_usage_analyzer import (
    analyze_names_in_function)
from pythagoras.___03_OLD_autonomous_functions.node_signatures import get_node_signature

from pythagoras.___03_OLD_autonomous_functions.pth_available_names_retriever import (
    retrieve_objs_available_inside_autonomous_functions)
from pythagoras._020_logging_portals.execution_environment_summary import (
    build_execution_environment_summary)


import pythagoras as pth


class CodePortal(DataPortal):

    node_id = get_node_signature()
    runtimes_to_clean = {}
    def __init__(
            self
            , base_dir:str
            , value_store:PersiDict
            , entropy_infuser:Random
            , execution_results:PersiDict
            , execution_requests:PersiDict
            , crash_history:PersiDict
            , event_log:PersiDict
            , run_history:OverlappingMultiDict
            , compute_nodes:OverlappingMultiDict
            , default_island_name:str
            , n_background_workers:int
            , runtime_id:str = None
            ):

        assert isinstance(execution_results, PersiDict)
        assert isinstance(execution_requests, PersiDict)
        assert isinstance(run_history, OverlappingMultiDict)
        assert isinstance(compute_nodes, OverlappingMultiDict)

        self.execution_results = execution_results
        self.execution_requests = execution_requests
        self.run_history = run_history
        self.compute_nodes = compute_nodes
        self.default_island_name = default_island_name
        self.n_background_workers = n_background_workers

        self.all_autonomous_functions = {default_island_name: {}}

        if runtime_id is None:
            runtime_id = get_random_signature()
            self.runtime_id = runtime_id
            self.runtimes_to_clean[runtime_id] = self
            self.compute_nodes.pkl[self.node_id, "runtime_id"] = runtime_id
            summary = build_execution_environment_summary()
            self.compute_nodes.json[self.node_id, "execution_environment"] = summary
        else:
            self.runtime_id = runtime_id

        super().__init__(base_dir=base_dir
                        , value_store=value_store
                        , entropy_infuser=entropy_infuser
                        , crash_history=crash_history
                        , event_log=event_log)

    def clean_runtime_id(self):
        """ Clean runtime id."""
        try:
            node_id = self.node_id
            address = [node_id, "runtime_id"]
            self.compute_nodes.pkl.delete_if_exists(address)
        except:
            pass

    def clear(self) -> None:
        super()._clear()
        self.clean_runtime_id()
        self.execution_results = None
        self.execution_requests = None
        self.crash_history = None
        self.event_log = None
        self.run_history = None
        self.compute_nodes = None
        self.default_island_name = None
        self.n_background_workers = None
        self.all_autonomous_functions = None

    def is_correctly_initialized(self) -> bool:
        result = super().is_correctly_initialized()
        result &= isinstance(self.execution_results, PersiDict)
        result &= isinstance(self.execution_requests, PersiDict)
        result &= isinstance(self.crash_history, PersiDict)
        result &= isinstance(self.event_log, PersiDict)
        result &= isinstance(self.run_history, OverlappingMultiDict)
        result &= isinstance(self.compute_nodes, OverlappingMultiDict)
        result &= isinstance(self.default_island_name, str)
        result &= isinstance(self.n_background_workers, int)
        result &= (self.n_background_workers >= 0)
        result &= isinstance(self.all_autonomous_functions, dict)
        if not result:
            return False

        if len(self.all_autonomous_functions) > 0:  # TODO: rework later
            for island_name in self.all_autonomous_functions:
                if not isinstance(island_name, str):
                    return False
                island = self.all_autonomous_functions[island_name]
                if not isinstance(island, dict):
                    return False
                for function_name in island:
                    if not isinstance(function_name, str):
                        return False
                    if not isinstance(island[function_name], pth.AutonomousFn):
                        return False

        return True

@atexit.register
def clean_all_runtime_ids():
    """ Clean all active runtime ids."""
    for runtime_id in CodePortal.runtimes_to_clean:
        try:
            portal = CodePortal.runtimes_to_clean[runtime_id]
            pythagoras._080_multiprocessing_portals.clean_runtime_id.clean_runtime_id()
        except:
            pass
    CodePortal.runtimes_to_clean = {}


class AutonomousFn(OrdinaryFn, PortalAwareClass):
    island_name:str
    strictly_autonomous:bool

    def __init__(self, a_fn: Callable | str | OrdinaryFn
                 , island_name:str | None = None
                 , strictly_autonomous:bool = False
                 , portal:CodePortal | None = None):

        assert isinstance(portal, CodePortal)

        OrdinaryFn.__init__(self,a_fn)
        PortalAwareClass.__init__(self, portal)

        if island_name is None:
            island_name = portal.default_island_name
        assert isinstance(island_name, str)
        # TODO: Add checks for island_name (should be a safe str)

        if isinstance(a_fn, AutonomousFn):
            assert island_name == a_fn.island_name

        self.island_name = island_name

        self.strictly_autonomous = bool(strictly_autonomous)

        if self.__class__.__name__ == AutonomousFn.__name__:
            with self.portal:
                register_autonomous_function(self)


    @property
    def portal(self) -> CodePortal:
        return super().portal

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
        portal = self.portal
        island = portal.all_autonomous_functions[self.island_name]
        name = self.fn_name
        assert island[name]._dependencies is not None
        result = island[name]._dependencies
        assert isinstance(result,list)
        assert len(result) >= 1
        if self.strictly_autonomous:
            assert len(result) == 1
        return sorted(result)

    def perform_initial_checks(self)-> bool:
        portal = self.portal
        island = portal.all_autonomous_functions[self.island_name]
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

        #TODO: add checks for strict autonomicity

        self._static_checks_passed = True
        return True

    def perform_runtime_checks(self)-> bool:
        portal = self.portal
        island = portal.all_autonomous_functions[self.island_name]
        fn_name = self.fn_name

        if island[fn_name]._runtime_checks_passed is not None:
            assert isinstance(island[fn_name]._runtime_checks_passed, bool)
            return island[fn_name]._runtime_checks_passed

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
        import_required -= {fn_name}
        if not self.strictly_autonomous:
            island = portal.all_autonomous_functions[self.island_name]
            prev_len_import_required = len(import_required)
            import_required -= set(island)
            if len(import_required) == prev_len_import_required:
                self.strictly_autonomous = True

        assert len(import_required) ==0, (f"Function {self.fn_name}"
            + f" is not autonomous, it uses global"
            + f" objects {import_required}"
            + f" without importing them inside the function body")

        all_functions_in_island = [f.fn_source_code for f in island.values()]
        deep_dependencies = explore_call_graph_deep(all_functions_in_island)
        dependencies = deep_dependencies[fn_name]
        assert isinstance(dependencies, set)
        assert len(dependencies) >= 1
        island[fn_name]._dependencies = sorted(dependencies)
        island[fn_name]._runtime_checks_passed = True
        return True


    def execute(self, **kwargs) -> Any:
        portal = self.portal
        try:
            runtime_checks_result = self.perform_runtime_checks()
            assert runtime_checks_result
            names_dict = retrieve_objs_available_inside_autonomous_functions()
            island = portal.all_autonomous_functions[self.island_name]
            names_dict["_pth_kwargs"] = kwargs
            if self.island_name is not None:
                for f_name in self.dependencies:
                    names_dict[f_name] = island[f_name]
            else: #TODO: remove legacy code
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
                DataPortal.log_exception(exception_id=exception_id)
            raise e

    # def __call__(self,* args, **kwargs) -> Any:
    #     assert len(args) == 0, (f"Function {self.fn_name} can't"
    #         + " be called with positional arguments,"
    #         + " only keyword arguments are allowed.")
    #     return self.execute(**kwargs)

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
        self.capture_portal()
        register_autonomous_function(self)



def register_autonomous_function(a_fn: AutonomousFn) -> None:
    """Register an autonomous function in the portal."""
    assert isinstance(a_fn, AutonomousFn)
    portal = a_fn.portal
    island_name = a_fn.island_name
    fn_name = a_fn.fn_name
    if island_name not in portal.all_autonomous_functions:
        portal.all_autonomous_functions[island_name] = dict()
    island = portal.all_autonomous_functions[island_name]
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

    initial_check_results = a_fn.perform_initial_checks()

    # if a_fn.strictly_autonomous:
    #     check_results &= a_fn.perform_runtime_checks()

    assert initial_check_results

    assert a_fn.island_name in portal.all_autonomous_functions
    assert a_fn.fn_name in portal.all_autonomous_functions[island_name]
    assert a_fn.fn_source_code == (
        portal.all_autonomous_functions[a_fn.island_name][a_fn.fn_name].fn_source_code)
    assert hasattr(portal.all_autonomous_functions[a_fn.island_name][a_fn.fn_name]
                   , "_static_checks_passed")
    assert hasattr(portal.all_autonomous_functions[a_fn.island_name][a_fn.fn_name]
                   , "_runtime_checks_passed")
    assert hasattr(portal.all_autonomous_functions[a_fn.island_name][a_fn.fn_name]
                   , "_dependencies")
    if a_fn is not portal.all_autonomous_functions[a_fn.island_name][a_fn.fn_name]:
        assert not hasattr(a_fn, "_static_checks_passed")
        assert not hasattr(a_fn, "_runtime_checks_passed")
        assert not hasattr(a_fn, "_dependencies")