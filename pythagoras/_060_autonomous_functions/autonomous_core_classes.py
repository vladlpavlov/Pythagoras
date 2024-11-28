from __future__ import annotations

import builtins
# from sys import Exception
from typing import Callable, Any

import pandas as pd
from persidict import FileDirDict

from pythagoras import LoggingPortal
from pythagoras._010_basic_portals import BasicPortal, PortalAwareClass
from pythagoras._010_basic_portals.foundation import _runtime
from pythagoras._020_logging_portals.logging_portals import NeedsRandomization

from pythagoras._030_data_portals.data_portals import DataPortal

from pythagoras._040_ordinary_functions.ordinary_funcs import (
    OrdinaryFn)

from pythagoras._060_autonomous_functions.call_graph_explorer import (
    explore_call_graph_deep)

from pythagoras._060_autonomous_functions.names_usage_analyzer import (
    analyze_names_in_function)

from pythagoras._050_safe_functions.safe_funcs import SafeFn


from pythagoras._060_autonomous_functions.pth_available_names_retriever import (
    retrieve_objs_available_inside_autonomous_functions)

import pythagoras as pth


class AutonomousCodePortal(DataPortal):
    
    default_island_name: str | None
    known_functions: dict[str, dict[str, AutonomousFn]] | None
    
    def __init__(
            self
            , base_dir: str | None = None
            , dict_type: type = FileDirDict
            , default_island_name: str = "Samos"
            , p_consistency_checks: float | None = None
            ):
        super().__init__(base_dir=base_dir
                         ,dict_type=dict_type
                         ,p_consistency_checks=p_consistency_checks)
        assert isinstance(default_island_name, str)
        assert len(default_island_name) >= 1
        self.default_island_name = default_island_name
        self.known_functions = dict()
        self.known_functions[default_island_name] = dict()

    def get_params(self) -> dict:
        """Get the portal's configuration parameters"""
        params = super().get_params()
        params["default_island_name"] = self.default_island_name
        return params

    def describe(self) -> pd.DataFrame:
        """Get a DataFrame describing the portal's current state"""
        all_params = [super().describe()]

        all_params.append(_runtime(
            "Islands"
            , len(self.known_functions)))
        all_params.append(_runtime(
            "Default island"
            , self.default_island_name))
        all_params.append(_runtime(
            "All islands"
            , ", ".join(list(self.known_functions))))
        for island_name, island in self.known_functions.items():
            n_functions = len(island)
            all_params.append(_runtime(
                f"Functions in <{island_name}>", n_functions))
            if n_functions > 0:
                all_params.append(_runtime(
                    f"Functions in <{island_name}>"
                    , ", ".join(list(island))))

        result = pd.concat(all_params)
        result.reset_index(drop=True, inplace=True)
        return result


    def _clear(self) -> None:
        """Clear the portal's state"""
        self.default_island_name = None
        self.known_functions = dict()
        super()._clear()

    @classmethod
    def get_portal(cls, suggested_portal: AutonomousCodePortal | None = None
                   ) -> AutonomousCodePortal:
        return BasicPortal.get_portal(suggested_portal)

    @classmethod
    def get_current_portal(cls) -> AutonomousCodePortal | None:
        """Get the current (default) portal object"""
        return BasicPortal._current_portal(expected_class=cls)

    @classmethod
    def get_noncurrent_portals(cls) -> list[AutonomousCodePortal]:
        return BasicPortal._noncurrent_portals(expected_class=cls)

    @classmethod
    def get_active_portals(cls) -> list[AutonomousCodePortal]:
        return BasicPortal._active_portals(expected_class=cls)



class AutonomousFn(SafeFn, PortalAwareClass):
    island_name:str
    strictly_autonomous:bool
    _autonomous_fn_dependencies: list[str] | None

    def __init__(self, a_fn: Callable | str | OrdinaryFn
                 , island_name:str | None = None
                 , strictly_autonomous:bool = False
                 , portal: AutonomousCodePortal | None = None):

        PortalAwareClass.__init__(self, portal=portal)
        SafeFn.__init__(self,a_fn)

        if island_name is None:
            island_name = self.portal.default_island_name
        assert isinstance(island_name, str)
        # TODO: Add checks for island_name (should be a safe str)

        if isinstance(a_fn, AutonomousFn):
            assert island_name == a_fn.island_name
            self.update(a_fn)
            return

        self.island_name = island_name
        self.strictly_autonomous = bool(strictly_autonomous)
        if type(self) == AutonomousFn:
            self._begin_fn_registration()

    def update(self, other: AutonomousFn) -> None:
        SafeFn.update(self, other)
        self.island_name = other.island_name
        self.strictly_autonomous = other.strictly_autonomous
        if other._fn_fully_registered:
            self._autonomous_fn_dependencies = other._autonomous_fn_dependencies


    def _begin_fn_registration(self) -> None:
        """Register an autonomous function in AutonomousCodePortal."""
        self._fn_fully_registered = False
        portal = self.portal
        island_name = self.island_name
        fn_name = self.fn_name
        if island_name not in portal.known_functions:
            portal.known_functions[island_name] = dict()
        island = portal.known_functions[island_name]

        if fn_name in island:
            assert self.fn_source_code == island[fn_name].fn_source_code, (
                    f"Function {fn_name} is already "
                    + f"defined in island {island_name}"
                    + f" with different source code. You cannot change it within"
                    + f" one session of the program.")
            assert self.decorator == island[fn_name].decorator, (
                    f"Function {fn_name} is already "
                    + f"defined in island {island_name} with the same source code "
                    + f"but different decorator. You cannot change decorator "
                    + f"within one session of the program.")
            assert type(self) == type(island[fn_name])
            self.update(island[fn_name])
            return

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

        # TODO: add checks for strict autonomicity

        island[fn_name] = self


    @property
    def portal(self) -> AutonomousCodePortal:
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
        island = portal.known_functions[self.island_name]
        name = self.fn_name
        assert island[name]._autonomous_fn_dependencies is not None
        result = island[name]._autonomous_fn_dependencies
        assert isinstance(result,list)
        assert len(result) >= 1
        if self.strictly_autonomous:
            assert len(result) == 1
        return sorted(result)


    def _complete_fn_registration(self)-> None:
        if self._fn_fully_registered:
            return

        portal = self.portal
        # if self.island_name not in portal.known_functions:
        #     portal.known_functions[self.island_name] = dict()
        assert self.island_name in portal.known_functions, (
            f"Island {self.island_name} was supposed to be pre-registered "
            f"in the portal")

        island = portal.known_functions[self.island_name]
        fn_name = self.fn_name
        assert fn_name in island, (f"Function {fn_name} was supposed "
            + f" to be pre-registered in island {self.island_name}")
        # if fn_name not in island:
        #     island[fn_name] = self
        assert self.fn_source_code == island[fn_name].fn_source_code

        if island[fn_name]._fn_fully_registered:
            if type(self) == AutonomousFn:
                self.update(island[fn_name])
            return

        SafeFn._complete_fn_registration(self)

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
        import_required -= {"self"} #TODO: replace with ._available_names() ???
        if not self.strictly_autonomous:
            island = portal.known_functions[self.island_name]
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
        dependencies = sorted(dependencies)
        island[fn_name]._autonomous_fn_dependencies = dependencies
        self._autonomous_fn_dependencies = dependencies

        if type(self) == AutonomousFn:
            self._fn_fully_registered = True
            island[fn_name]._fn_fully_registered = True


    def _available_names(self):
        all_names = super()._available_names()
        island = self.portal.known_functions[self.island_name]
        for name in self.dependencies:
            all_names[name] = island[name]
        return all_names

    def _exception_prefixes(self) -> list[list[str]]:
        return [[f"{self.fn_name}_{self.island_name}_AUTON"]
            ] + LoggingPortal._exception_prefixes()

    def _exception_id(self, exc_value) -> str:
        return NeedsRandomization(
            super()._exception_id(exc_value)
            + f"_{self.island_name}")


    def _extra_exception_data(self) -> dict:
        result = dict(
            function_name=self.fn_name
            ,island_name = self.island_name
            ,dependencies = self.dependencies
            )
        result |= super()._extra_exception_data()
        return result

    def execute(self, **kwargs) -> Any:
        with self.portal as portal:
            return SafeFn.execute(self, **kwargs)

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
        assert type(self) == AutonomousFn
        assert state["class_name"] == AutonomousFn.__name__
        self.fn_name = state["fn_name"]
        self.fn_source_code = state["fn_source_code"]
        self.island_name = state["island_name"]
        self.strictly_autonomous = state["strictly_autonomous"]
        self._fn_fully_registered = False
        self.capture_portal()
        self._begin_fn_registration()