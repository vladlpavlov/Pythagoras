from __future__ import annotations

from typing import Callable, Optional, Any

import pythagoras as pth
from pythagoras._01_foundational_objects.hash_addresses import get_hash_signature
from pythagoras._03_autonomous_functions import AutonomousFunction
from pythagoras._04_idempotent_functions.kw_args import UnpackedKwArgs

# from pythagoras._05_mission_control import (
#     register_idempotent_function
#     , get_all_cloudized_function_names
#     , get_cloudized_function)

from pythagoras._03_autonomous_functions.call_graph_explorer import (
    explore_call_graph_deep)

class IdempotentFunction:
    def __init__(self,a_func:Callable, island_name:Optional[str]=None):
        if island_name is None:
            island_name = pth.default_island_name
        self.island_name = island_name
        assert callable(a_func)
        assert not pth.accepts_unlimited_positional_args(a_func)
        if not isinstance(a_func, AutonomousFunction):
            a_func = AutonomousFunction(a_func, island_name)
        # self.autonomous_function = a_func
        self.function_source = a_func.function_source
        self.function_name = a_func.function_name
        self._augmented_function_source = None
        self._augmented_function_code = None
        register_idempotent_function(self)

    @property
    def decorator(self) -> str:
        return f"@pth.idempotent(island_name={self.island_name})"

    def _build_augmented_source_and_code(self) -> None:

        # assert (self._augmented_function_source is None) == (
        #     self._augmented_function_code is None)
        if self._augmented_function_source is not None:
            return

        self.autonomous_function.check_autonomous_requirements(
            island_name=self.island_name)
        assert self.autonomous_function.checks_passed

        default_decorator = ("@pth.idempotent" +
            f"(island_name={self.island_name})\n")

        available_function_names = get_all_cloudized_function_names(
            island_name=self.island_name)
        available_function_srcs = []
        for function_name in available_function_names:
            available_function_srcs += [get_cloudized_function(
                function_name=function_name,island_name=self.island_name
                    ).function_source]
        call_graph = explore_call_graph_deep(available_function_srcs)
        dependencies = sorted(call_graph[self.function_name])
        self._augmented_function_source = ""
        for function_name in dependencies:
            new_src = get_cloudized_function(
                function_name=function_name,island_name=self.island_name
                    ).function_source
            if not new_src.startswith("@"):
                new_src = default_decorator + new_src
            # if function_name == self.function_name:
            #     new_src = get_normalized_function_source(
            #         new_src, drop_decorators=True)
            self._augmented_function_source += new_src + "\n"
        # self._augmented_function_source += f"\n_={self.function_name}(**_)"

        self._build_augmented_function_code()


    def _build_augmented_function_code(self) -> None:
        name = self.function_name.lower()
        filename = get_hash_signature(self)[:8] + "_" + name
        self._augmented_function_filename = filename
        source_to_execute = self._augmented_function_source
        self._augmented_function_code = compile(
            source_to_execute, f"{filename}.py", "exec")
        name = self.function_name.lower()
        location = (name, self._augmented_function_filename)
        pth.function_source_repository[
            location] = self._augmented_function_source


    @property
    def augmented_function_source(self) -> str:
        self._build_augmented_source_and_code()
        return self._augmented_function_source

    @property
    def augmented_function_code(self):
        self._build_augmented_source_and_code()
        return self._augmented_function_code


    def __getstate__(self):
        draft_state = dict(island_name=self.island_name
            , function_name=self.function_name
            , function_source=self.function_source
            , augmented_function_source = self.augmented_function_source)
        state = dict()
        for key in sorted(draft_state):
            state[key] = draft_state[key]
        return state

    def __setstate__(self, state):
        assert len(state) == 4
        self.island_name = state["island_name"]
        self.function_name = state["function_name"]
        self.function_source = state["function_source"]
        self._augmented_function_source = state["augmented_function_source"]
        self._build_augmented_function_code()
        self.autonomous_function = None
        register_idempotent_function(self)


    def _call_bare_original(self, **kwargs) -> Any:
        kw_args = UnpackedKwArgs(**kwargs)
        # variables = dict(_ = kw_args)
        # exec(self.augmented_function_code,variables,variables)
        # result= variables["_"]
        source_to_execute = self.function_source
        # source_to_execute = source_to_execute.replace(
        #     self.function_name, "_")
        source_to_execute += f"\n_={self.function_name}"
        _, result = None , None
        variables = dict(globals())
        variables |= locals()
        exec(source_to_execute, variables, variables)
        result = variables["_"](**kw_args)
        return result

    def _call_augmented_original(self, **kwargs) -> Any:
        kw_args = UnpackedKwArgs(**kwargs)
        variables = dict(_ = kw_args)
        source_to_execute = self.augmented_function_source
        first_line = "import pythagoras as pth\n"
        last_line = f"\n_={self.function_name}._call_bare_original(**_)"
        source_to_execute = first_line + source_to_execute + last_line

        exec(source_to_execute,variables,variables)
        result= variables["_"]
        return result


    def __call__(self,**kwargs) -> Any:
        return self._call_bare_original(**kwargs)


    # @property
    # def island_name(self)->str:
    #     pass
    #
    # @property
    # def function_name(self) -> str:
    #     pass
    #
    # @property
    # def validator_src(self) -> str:
    #     pass
    #
    # @property
    # def corrector_src(self) -> str:
    #     pass
    #
    # @property
    # def function_src(self) -> str:
    #     return self.__normaized_f_source__
    #
    # @property
    # def subisland_src(self) -> str:
    #     pass



    #
    #
    # def _inprocess_many(self, *args) -> List[Any]:
    #     pass
    #
    #
    # def _subprocess(self, **kwargs) -> Any:
    #     pass
    #
    #
    # def _subprocess_many(self, *args) -> List[Any]:
    #     pass


    # def _enqueue(self, **kwargs) -> CloudFuncOutputAddress:
    #     pass
    #
    #
    # def _enqueue_many(self, *args) -> List[CloudFuncOutputAddress]:
    #     pass
    #
    # def parallel(self, args) -> List[Any]:
    #     pass
    #
    #
    # def __getstate__(self):
    #     self.subisland_src
    #     return self.__dict__
