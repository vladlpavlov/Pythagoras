from __future__ import annotations
from pythagoras.misc_utils.global_state_management import (
    get_all_cloudized_function_names, get_cloudized_function
    , register_cloudized_function)
from pythagoras.foundational_objects.kw_args import PackedKwArgs
import pythagoras as pth


from typing import Callable, Any, Optional

from pythagoras.function_decorators.autonomous_funcs import (
    LooselyAutonomousFunction, AutonomousFunction)
from pythagoras.python_utils import explore_call_graph_deep, \
    get_normalized_function_source


class CloudizedFunction:
    def __init__(self,a_func:Callable, island_name:Optional[str]=None):
        if island_name is None:
            island_name = pth.default_island_name
        self.island_name = island_name
        assert callable(a_func)
        if not isinstance(a_func, AutonomousFunction):
            a_func = LooselyAutonomousFunction(a_func, island_name)
        self.autonomous_function = a_func
        self.function_source = a_func.function_source
        self.function_name = a_func.function_name
        self._augmented_function_source = None
        self._augmented_function_code = None
        register_cloudized_function(self)

    def _build_augmented_source_and_code(self) -> None:

        assert (self._augmented_function_source is None) == (
            self._augmented_function_code is None)
        if self._augmented_function_source is not None:
            return

        self.autonomous_function.check_autonomous_requirements(
            island_name=self.island_name)
        assert self.autonomous_function.checks_passed is True

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
            if function_name == self.function_name:
                new_src = get_normalized_function_source(
                    new_src, drop_decorators=True)
            self._augmented_function_source += new_src + "\n"
        self._build_augmented_function_code()


    def _build_augmented_function_code(self) -> None:
        # TODO: check this  vvvvvv
        source_to_execute = self._augmented_function_source
        source_to_execute += (f"\n__pth_result__={self.function_name}"
                              + "(**__pth_kwargs__)\n")
        self._augmented_function_code = compile(
            source_to_execute, f"AUGMENTED:{self.function_name}", "exec")
        # TODO: check this  ^^^^^^

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
        register_cloudized_function(self)


    def _naked_call(self, **kwargs) -> Any:
        kw_args = PackedKwArgs(**kwargs).unpack()
        variables = dict(__pth_kwargs__ = kw_args)
        exec(self.augmented_function_code,variables,variables)
        result= variables["__pth_result__"]
        return result


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
    # def __call__(self,**kwargs) -> Any:
    #     return self._inprocess(**kwargs)
    #
    # def __getstate__(self):
    #     self.subisland_src
    #     return self.__dict__
