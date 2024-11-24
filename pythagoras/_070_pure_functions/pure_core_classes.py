from __future__ import annotations

import os
import time
import traceback
from copy import copy
from typing import Callable, Any, List, TypeAlias

import pandas as pd
from sklearn.model_selection import ParameterGrid

from persidict import PersiDict, FileDirDict

from pythagoras import OverlappingMultiDict, LoggingPortal
from pythagoras import PortalAwareClass, BasicPortal
from pythagoras._010_basic_portals.foundation import _persistent
from pythagoras._820_strings_signatures_converters.random_signatures import (
    get_random_signature)
from pythagoras._800_persidict_extensions.first_entry_dict import FirstEntryDict
from pythagoras._020_logging_portals.logging_portals import NeedsRandomization, AlreadyRandomized

from pythagoras._030_data_portals.hash_addresses import HashAddr
from pythagoras._030_data_portals.value_addresses import ValueAddr

from pythagoras._060_autonomous_functions.autonomous_core_classes import (
    AutonomousFn, AutonomousCodePortal)

from pythagoras._040_ordinary_functions.ordinary_funcs import (
    OrdinaryFn)

from pythagoras._070_pure_functions.kw_args import SortedKwArgs
from pythagoras._070_pure_functions.process_augmented_func_src import (
    process_augmented_func_src)
from pythagoras._810_output_manipulators.output_capturer import OutputCapturer
from pythagoras._020_logging_portals.execution_environment_summary import (
    build_execution_environment_summary)



ASupportingFunc:TypeAlias = str | AutonomousFn

SupportingFuncs:TypeAlias = ASupportingFunc | List[ASupportingFunc] | None


class PureCodePortal(AutonomousCodePortal):

    known_functions: dict[str, dict[str, PureFn]] | None

    execution_results: FirstEntryDict | None
    execution_requests: PersiDict | None
    run_history: OverlappingMultiDict | None

    def __init__(
            self
            , base_dir: str | None = None
            , dict_type: type = FileDirDict
            , default_island_name: str = "Samos"
            , p_consistency_checks: float | None = None
            ):
        super().__init__(base_dir=base_dir
                         , dict_type=dict_type
                         , default_island_name=default_island_name
                         , p_consistency_checks=p_consistency_checks)
        execution_results_dir = os.path.join(
            base_dir, "execution_results")
        execution_results = dict_type(
            execution_results_dir, digest_len=0
            , immutable_items=True)
        execution_results = FirstEntryDict(
            execution_results, p_consistency_checks)
        self.execution_results = execution_results

        execution_requests_dir = os.path.join(
            base_dir, "execution_requests")
        execution_requests = dict_type(
            execution_requests_dir, digest_len=0
            , immutable_items=False)
        self.execution_requests = execution_requests

        run_history_dir = os.path.join(
            base_dir, "run_history")
        run_history = OverlappingMultiDict(
            dict_type=dict_type
            , dir_name=run_history_dir
            , json=dict(digest_len=0, immutable_items=True)
            , py=dict(
                base_class_for_values=str
                , digest_len=0
                , immutable_items=False)
            , txt=dict(
                base_class_for_values=str
                , digest_len=0
                , immutable_items=True)
            , pkl=dict(
                digest_len=0
                , immutable_items=True) 
            )
        self.run_history = run_history


    def describe(self) -> pd.DataFrame:
        """Get a DataFrame describing the portal's current state"""
        all_params = [super().describe()]

        all_params.append(_persistent(
            "Cached execution results"
            , len(self.execution_results)))
        all_params.append(_persistent(
            "Execution queue size"
            , len(self.execution_requests)))

        result = pd.concat(all_params)
        result.reset_index(drop=True, inplace=True)
        return result

    def _clear(self):
        self.execution_results = None
        self.execution_requests = None
        self.run_history = None
        super()._clear()


    @classmethod
    def get_portal(cls, suggested_portal: PureCodePortal | None = None
                   ) -> PureCodePortal:
        return BasicPortal.get_portal(suggested_portal)

    @classmethod
    def get_current_portal(cls) -> PureCodePortal | None:
        """Get the current (default) portal object"""
        return BasicPortal._current_portal(expected_class=cls)

    @classmethod
    def get_noncurrent_portals(cls) -> list[PureCodePortal]:
        return BasicPortal._noncurrent_portals(expected_class=cls)

    @classmethod
    def get_active_portals(cls) -> list[PureCodePortal]:
        return BasicPortal._active_portals(expected_class=cls)



class PureFn(AutonomousFn):

    _augmented_source_code: str | None
    guards: SupportingFuncs
    call_stack:list[PureFnExecutionFrame]
    def __init__(self, a_fn: Callable | str | OrdinaryFn
                 , island_name:str | None = None
                 , guards: SupportingFuncs = None
                 , portal: PureCodePortal | None = None):
        super().__init__(a_fn, island_name = island_name, portal = portal)
        self.guards = self._preprocess_guards(guards)
        self._augmented_source_code = None
        #TODO: decide how to handle guards if a_fn is PureFn
        self.call_stack = []
        if type(self) == PureFn:
            self._begin_fn_registration()

    @property
    def portal(self) -> PureCodePortal:
        return super().portal

    def update(self, other: PureFn) -> None:
        super().update(other)
        self.guards = other.guards
        self._augmented_source_code = other._augmented_source_code
        self.call_stack = other.call_stack


    def _preprocess_guards(self
            , supporting_funcs: SupportingFuncs = None
            ) -> List[str]|None:
        guards_list = None
        if supporting_funcs is None:
            return guards_list
        if isinstance(supporting_funcs, (AutonomousFn, str)):
            guards_list = [supporting_funcs]
        else:
            guards_list = supporting_funcs
        assert isinstance(guards_list, list)
        result_names = []
        island = self.portal.known_functions[self.island_name]
        for f in guards_list:
            if isinstance(f, AutonomousFn):
                assert f.strictly_autonomous
                assert f.island_name == self.island_name
                assert f.portal == self.portal
                result_names.append(f.fn_name)
            else:
                assert isinstance(f, str)
                assert f in island
                result_names.append(f)
        result_names = sorted(result_names)
        return result_names


    def can_be_executed(self,**kwargs) -> bool:
        """Indicates if the function can be executed in the current environment.
        """
        with self.portal:
            try:
                if self.guards is not None:
                    island = self.portal.known_functions[self.island_name]
                    for f in self.guards:
                        island[f].execute(**kwargs)
                return True
            except:
                return False




    @property
    def fn_type(self) -> str:
        return "pure"

    @property
    def decorator(self) -> str:
        decorator_str = "@pth.pure("
        decorator_str += f"\n\tisland_name='{self.island_name}'"
        if self.guards is not None:
            guards_str = f"\n\t, guards={self.guards}"
            decorator_str += guards_str
        decorator_str += ")"
        return decorator_str

    def _complete_fn_registration(self):
        if self._fn_fully_registered:
            return
        super()._complete_fn_registration()
        island_name = self.island_name
        assert island_name in self.portal.known_functions
        island = self.portal.known_functions[island_name]

        augmented_code = ""

        full_dependencies = []
        if self.guards is not None:
            full_dependencies += self.guards
        full_dependencies += self.dependencies
        full_dependencies = sorted(full_dependencies)

        for fn_name in full_dependencies:
            f = island[fn_name]
            augmented_code += f.decorator + "\n"
            augmented_code += f.fn_source_code + "\n"
            augmented_code += "\n"

        name = self.fn_name
        assert hasattr(island[name], "_augmented_source_code")
        if island[name]._augmented_source_code is None:
            island[name]._augmented_source_code = augmented_code
        else:
            assert island[name]._augmented_source_code == augmented_code

        self._augmented_source_code = augmented_code

        if type(self) == PureFn:
            self._fn_fully_registered = True
            island[name]._fn_fully_registered = True



    @property
    def augmented_fn_source_code(self) -> str:
        """The augmented source code of the function.

        The augmented source code of a pure function
        includes the source code of the function itself,
        as well as the source code of all the autonomous functions
        it depends on, including guards.
        """
        assert self._fn_fully_registered
        island_name = self.island_name
        island = self.portal.known_functions[island_name]
        assert hasattr(island[self.fn_name], "_augmented_source_code")
        assert island[self.fn_name]._augmented_source_code is not None
        return island[self.fn_name]._augmented_source_code


    def __getstate__(self):
        """Return the state of the object for pickling. """
        self._complete_fn_registration()
        draft_state = dict(fn_name=self.fn_name
            , fn_source_code=self.fn_source_code
            , island_name=self.island_name
            , augmented_fn_source_code=self.augmented_fn_source_code
            , strictly_autonomous=self.strictly_autonomous
            , guards=self.guards
            )
        state = dict()
        for key in sorted(draft_state):
            state[key] = draft_state[key]
        return state

    def __setstate__(self, state):
        """Set the state of the object from a pickled state."""
        assert len(state) == 6
        assert type(self) == PureFn
        self.fn_name = state["fn_name"]
        self.fn_source_code = state["fn_source_code"]
        self.island_name = state["island_name"]
        self.strictly_autonomous = state["strictly_autonomous"]
        self.guards = state["guards"]
        self._augmented_source_code = None
        self._portal = None
        self.capture_portal()
        self.call_stack = list()
        self._begin_fn_registration()

        with self.portal as portal:
            island_name = self.island_name
            island = self.portal.known_functions[island_name]
            fn_name = self.fn_name
            if not island[fn_name]._fn_fully_registered:
                island[fn_name]._augmented_source_code = (
                    state["augmented_fn_source_code"])
                process_augmented_func_src(
                    state["augmented_fn_source_code"], portal=portal)
            else:
                assert state["augmented_fn_source_code"] == (
                    island[fn_name]._augmented_source_code)

        self._complete_fn_registration()


    def _exception_prefixes(self) -> list[list[str]]:
        return [[f"{self.fn_name}_{self.island_name}_PURE"]
            ] + LoggingPortal._exception_prefixes()

    def _extra_exception_data(self) -> dict:
        result = dict(
            function_name=self.fn_name
            ,island_name = self.island_name
            ,guards = self.guards
            ,dependencies = self.dependencies
            ,augmented_source_code = self._augmented_source_code.replace("\t",4*" ").split("\n")
            )
        if len(self.call_stack):
            result |= self.call_stack[-1]._extra_exception_data()
        result |= super()._extra_exception_data()
        return result

    def _exception_id(self, exc_value) -> str:
        exception_id = super()._exception_id(exc_value)
        if len(self.call_stack):
            current_frame = self.call_stack[-1]
            exception_id += "_" + current_frame.session_id
            exception_id += "_" + str(current_frame.exception_counter)
            return AlreadyRandomized(exception_id)
        else:
            return NeedsRandomization(exception_id)

    def _persist_exception_information(self
           , exc_value, exc_type, trace_back
           , exception_id, exception_prefixes
           , exception_extra_data_to_persist) -> dict|None:
        data_to_persist = super()._persist_exception_information(
            exc_value=exc_value
            , exc_type=exc_type
            , trace_back=trace_back
            , exception_id=exception_id
            , exception_prefixes=exception_prefixes
            , exception_extra_data_to_persist=exception_extra_data_to_persist)
        if len(self.call_stack) and data_to_persist is not None:
            current_frame = self.call_stack[-1]
            current_frame.register_exception(exception_id = exception_id
                ,data_to_persist = data_to_persist)
        return data_to_persist


    def _begin_fn_registration(self) -> None:
        """Register an idempotent function in the Pythagoras system."""
        super()._begin_fn_registration()
        #TODO: do we need the below?
        island_name = self.island_name
        island = self.portal.known_functions[island_name]
        name = self.fn_name
        if not hasattr(island[name], "_augmented_source_code"):
            island[name]._augmented_source_code = None

    def get_address(self, **kwargs) -> PureFnExecutionResultAddr:
        with self.portal:
            packed_kwargs = SortedKwArgs(**kwargs).pack(self.portal)
            result_address = PureFnExecutionResultAddr(self, packed_kwargs)
            return result_address


    def swarm(self, **kwargs) -> PureFnExecutionResultAddr:
        """ Request execution of the function with the given arguments.

        The function is executed in the background. The result can be
        retrieved later using the returned address.
        """
        with self.portal:
            result_address = self.get_address(**kwargs)
            result_address.request_execution()
            return result_address

    def run(self, **kwargs) -> PureFnExecutionResultAddr:
        """ Execute the function with the given arguments.

        The function is executed immediately. The result can be
        retrieved later using the returned address.
        """
        with self.portal:
            result_address = self.get_address(**kwargs)
            result_address.execute()
            return result_address


    def execute(self, **kwargs) -> Any:
        """ Execute the function with the given arguments.

        The function is executed immediately and the result is returned.
        The result is memoized, so the function is actually executed
        only the first time it's called; subsequent calls return the
        cached result.
        """

        with self.portal as portal:
            packed_kwargs = SortedKwArgs(**kwargs).pack(portal)
            output_address = PureFnExecutionResultAddr(self, packed_kwargs)
            random_x = portal.entropy_infuser.random()
            p_consistency_checks = portal.p_consistency_checks
            conduct_consistency_checks = False
            if output_address.ready:
                if p_consistency_checks in [None,0]:
                    return output_address.get()
                if not random_x < p_consistency_checks:
                    return output_address.get()
                conduct_consistency_checks = True
            with PureFnExecutionFrame(output_address) as frame:
                output_address.request_execution()
                assert self.can_be_executed(**kwargs)
                unpacked_kwargs = SortedKwArgs(**packed_kwargs).unpack()
                result = super().execute(**unpacked_kwargs)
                result_addr = ValueAddr(result)
                frame.register_execution_result(result_addr)
                try:
                    if conduct_consistency_checks:
                        portal.execution_results._p_consistency_checks = 1
                    portal.execution_results[output_address] = result_addr
                except:
                    raise # TODO: raise a proper exception here
                finally:
                    portal.execution_results._p_consistency_checks = (
                        p_consistency_checks)
                output_address.drop_execution_request()
                return result

    def swarm_list(
            self
            , list_of_kwargs:list[dict]
            ) -> list[PureFnExecutionResultAddr]:
        assert isinstance(list_of_kwargs, (list, tuple))
        for kwargs in list_of_kwargs:
            assert isinstance(kwargs, dict)
        with self.portal:
            list_to_return = []
            list_to_swarm = []
            for kwargs in list_of_kwargs:
                new_addr = PureFnExecutionResultAddr(self, kwargs)
                list_to_return.append(new_addr)
                list_to_swarm.append(new_addr)
            self.portal.entropy_infuser.shuffle(list_to_swarm)
            for an_addr in list_to_swarm:
                an_addr.request_execution()
        return list_to_return

    def run_list(
            self
            , list_of_kwargs:list[dict]
            ) -> list[PureFnExecutionResultAddr]:
        with self.portal:
            addrs = self.swarm_list(list_of_kwargs)
            addrs_workspace = copy(addrs)
            self.portal.entropy_infuser.shuffle(addrs_workspace)
            for an_addr in addrs_workspace:
                an_addr.execute()
        return addrs

    def swarm_grid(
            self
            , grid_of_kwargs:dict[str, list] # refactor
            ) -> list[PureFnExecutionResultAddr]:
        with self.portal:
            param_list = list(ParameterGrid(grid_of_kwargs))
            addrs = self.swarm_list(param_list)
            return addrs

    def run_grid(
            self
            , grid_of_kwargs:dict[str, list] # refactor
            ) -> list[PureFnExecutionResultAddr]:
        with self.portal:
            param_list = list(ParameterGrid(grid_of_kwargs))
            addrs = self.run_list(param_list)
            return addrs


class PureFnCallSignature(PortalAwareClass):
    """A signature of a call to a pure function.

    This class is used to create a unique identifier for a call to a
    pure function. The identifier is used to store the result of the
    call in the value store.

    This is a supporting class for PureFnExecutionResultAddr.
    Pythagoras' users should not need to interact with it directly.
    """
    def __init__(self, a_fn:PureFn, arguments:SortedKwArgs):
        assert isinstance(a_fn, PureFn)
        assert isinstance(arguments, SortedKwArgs)
        portal = a_fn.portal
        super().__init__(portal=portal)
        with portal:
            self.fn_name = a_fn.fn_name
            self.island_name = a_fn.island_name
            self.fn_addr = ValueAddr(a_fn)
            self.args_addr = ValueAddr(arguments.pack(portal))

    def __getstate__(self):
        state = dict(
            fn_name=self.fn_name
            , fn_addr=self.fn_addr
            , island_name=self.island_name
            , args_addr=self.args_addr)
        return state

    def __setstate__(self, state):
        assert len(state) == 4
        self.fn_name = state["fn_name"]
        self.fn_addr = state["fn_addr"]
        self.island_name = state["island_name"]
        self.args_addr = state["args_addr"]
        self._portal = None
        self.capture_portal()

    @property
    def portal(self) -> PureCodePortal:
        return super().portal


class PureFnExecutionResultAddr(HashAddr):
    """An address of the result of an execution of a pure function.

    This class is used to point to the result of an execution of a pure
    function in a portal. The address is used to request an execution and
    to retrieve the result (if available) from the portal.

    The address also provides access to various logs and records of the
    function execution, such as environmental contexts of the execution attempts,
    outputs printed, exceptions thrown and events emitted.
    """

    def __init__(self, a_fn: PureFn, arguments:dict[str, Any]):
        assert isinstance(a_fn, PureFn)
        self._arguments = SortedKwArgs(**arguments)
        signature = PureFnCallSignature(a_fn, self._arguments)
        tmp = ValueAddr(signature)
        new_prefix = a_fn.fn_name
        if a_fn.island_name is not None:
            new_prefix += "_" + a_fn.island_name
        new_hash_value = tmp.hash_value
        super().__init__(new_prefix, new_hash_value, portal=a_fn.portal)
        self._function = a_fn

    @property
    def portal(self) -> PureCodePortal:
        return super().portal

    def _invalidate_cache(self):
        if hasattr(self, "_ready"):
            del self._ready
        if hasattr(self, "_function"):
            del self._function
        if hasattr(self, "_result"):
            del self._result
        if hasattr(self, "_arguments"):
            del self._arguments

    def get_ValueAddr(self):
        with self.portal as portal:
            return ValueAddr.from_strings(  # TODO: refactor this
                # prefix="idempotentfncallsignature"
                prefix = PureFnCallSignature.__name__.lower()
                , hash_value=self.hash_value
                , portal= portal)

    def __setstate__(self, state):
        assert len(state) == 1
        self.str_chain = state["str_chain"]
        self._invalidate_cache()
        self._portal = None
        self.capture_portal()


    def __getstate__(self):
        state = dict(str_chain=self.str_chain)
        return state

    @property
    def _ready_in_current_portal(self):
        """Indicates if the result of the function call is available."""
        if hasattr(self, "_ready"):
            return True
        with self.portal:
            result = (self in self.portal.execution_results)
            if result:
                self._ready = True
            return result

    @property
    def _ready_in_noncurrent_portals(self) -> bool:
        for portal in PureCodePortal.get_noncurrent_portals():
            with portal:
                if self in portal.execution_results:
                    addr = portal.execution_results[self]
                    data = portal.value_store[addr]
                    with self.portal:
                        self.portal.execution_results[self] = ValueAddr(data)
                        _ = self.function # needed for cross-portal sync
                        _ = self.kwargs # needed for cross-portal sync
                        # TODO: refactor ( implement self._function_ready ? )
                        # TODO: ( implement self._kwargs_ready ? )

                    self._ready = True
                    return True
        return False

    @property
    def ready(self) -> bool:
        if hasattr(self, "_ready"):
            assert self._ready
            return True
        if self._ready_in_current_portal:
            self._ready = True
            return True
        if self._ready_in_noncurrent_portals:
            self._ready = True
            return True
        return False

    def execute(self):
        """Execute the function and store the result in the portal."""
        if hasattr(self, "_result"):
            return self._result
        with self.portal:
            function = self.function
            arguments = self.arguments
            self._result = function.execute(**arguments)
            return self._result


    def request_execution(self):
        """Request execution of the function, without actually executing it."""
        with self.portal as portal:
            if self.ready:
                self.drop_execution_request()
            else:
                if self not in portal.execution_requests:
                    portal.execution_requests[self] = True


    def drop_execution_request(self):
        """Remove the request for execution of the function."""
        with self.portal:
            self.portal.execution_requests.delete_if_exists(self)


    @property
    def execution_requested(self):
        """Indicates if the function execution has been requested."""
        with self.portal:
            return self in self.portal.execution_requests


    def get(self, timeout: int = None):
        """Retrieve value, referenced by the address.

        If the value is not immediately available, backoff exponentially
        till timeout is exceeded. If timeout is None, keep trying forever.

        This method does not actually execute the function, but simply
        retrieves the result of the function execution, if it is available.
        If it is not available, the method waits for the result to become
        available, or until the timeout is exceeded.
        """
        assert timeout is None or timeout >= 0
        if hasattr(self, "_result"):
            return self._result

        with self.portal as portal:

            if self.ready:
                result_addr = portal.execution_results[self]
                self._result = portal.value_store[result_addr]
                return self._result

            self.request_execution()

            start_time, backoff_period = time.time(), 1.0
            if timeout is not None:
                stop_time = start_time + timeout
            else:
                stop_time = None
            # start_time, stop_time and backoff_period are in seconds

            while True:
                if self.ready:
                    result_addr = portal.execution_results[self]
                    self._result = portal.value_store[result_addr]
                    self.drop_execution_request()
                    return self._result
                else:
                    time.sleep(backoff_period)
                    backoff_period *= 2.0
                    backoff_period += portal.entropy_infuser.uniform(-0.5, 0.5)
                    if stop_time:
                        current_time = time.time()
                        if current_time + backoff_period > stop_time:
                            backoff_period = stop_time - current_time
                        if current_time > stop_time:
                            raise TimeoutError
                    backoff_period = max(1.0, backoff_period)

    @property
    def function(self) -> PureFn:
        """Return the function object referenced by the address."""
        if hasattr(self, "_function"):
            return self._function
        with self.portal:
            signature_addr = self.get_ValueAddr()
            signature = signature_addr.get()
            fn_addr = signature.fn_addr
            self._function = fn_addr.get()
            return self._function

    @property
    def fn(self) -> PureFn:
        """Return the function object referenced by the address."""
        with self.portal:
            return self.function


    @property
    def fn_name(self) -> str:
        """Return the name of the function referenced by the address."""
        with self.portal:
            signature_addr = self.get_ValueAddr()
            signature = signature_addr.get()
            return signature.fn_name


    @property
    def fn_source_code(self) -> str:
        """Return the source code of the function referenced by the address."""
        with self.portal:
            function = self.function
            return function.fn_source_code


    @property
    def island_name(self) -> str:
        """The name of the island of the function referenced by the address."""
        with self.portal:
            return self.function.island_name


    @property
    def arguments(self) -> SortedKwArgs:
        """Packed arguments of the function call, referenced by the address."""
        if hasattr(self, "_arguments"):
            return self._arguments
        with self.portal:
            signature_addr = self.get_ValueAddr()
            signature = signature_addr.get()
            self._arguments = signature.args_addr.get()
            return self._arguments


    @property
    def kwargs(self) -> dict:
        """Unpacked arguments of the function call, referenced by the address."""
        with self.portal as portal:
            return self.arguments.unpack()


    @property
    def can_be_executed(self) -> bool:
        """Indicates if the function can be executed in the current session.

        The function should fe refactored once we start fully supporting
        guards
        """
        with self.portal:
            return self.function.can_be_executed(**self.kwargs)


    @property
    def needs_execution(self) -> bool:
        """Indicates if the function is a good candidate for execution.

        Returns False if the result is already available, or if some other
        process is currently working on it. Otherwise, returns True.
        """
        DEFAULT_EXECUTION_TIME = 10
        MAX_EXECUTION_ATTEMPTS = 5
        # TODO: these should not be constants
        if self.ready:
            return False
        with self.portal:
            past_attempts = self.execution_attempts
            n_past_attempts = len(past_attempts)
            if n_past_attempts == 0:
                return True
            if n_past_attempts > MAX_EXECUTION_ATTEMPTS:
                #TODO: log this event. Should we have DLQ?
                return False
            most_recent_timestamp = max(
                past_attempts.timestamp(a) for a in past_attempts)
            current_timestamp = time.time()
            if (current_timestamp - most_recent_timestamp
                    > DEFAULT_EXECUTION_TIME*(2**n_past_attempts)):
                return True
            return False



    @property
    def execution_records(self) -> list[PureFnExecutionRecord]:
        with self.portal:
            result = []
            for k in self.execution_attempts:
                run_id = k[-1][:-2]
                result.append(PureFnExecutionRecord(self, run_id))
            return result


    @property
    def execution_attempts(self) -> PersiDict:
        with self.portal as portal:
            attempts_path = self + ["attempts"]
            attempts = portal.run_history.json.get_subdict(attempts_path)
            return attempts

    @property
    def last_execution_attempt(self) -> Any:
        with self.portal:
            attempts = self.execution_attempts
            timeline = attempts.newest_values()
            if not len(timeline):
                result = None
            else:
                result = timeline[0]
            return result

    @property
    def execution_results(self) -> PersiDict:
        with self.portal as portal:
            results_path = self + ["results"]
            results = portal.run_history.pkl.get_subdict(results_path)
            return results


    @property
    def execution_outputs(self) -> PersiDict:
        with self.portal as portal:
            outputs_path = self + ["outputs"]
            outputs = portal.run_history.txt.get_subdict(outputs_path)
            return outputs

    @property
    def last_execution_output(self) -> Any:
        with self.portal as portal:
            outputs = self.execution_outputs
            timeline = outputs.newest_values()
            if not len(timeline):
                result = None
            else:
                result = timeline[0]
            return result


    @property
    def crashes(self) -> PersiDict:
        with self.portal as portal:
            crashes_path = self + ["crashes"]
            crashes = portal.run_history.json.get_subdict(crashes_path)
            return crashes


    @property
    def last_crash(self) -> Any:
        with self.portal as portal:
            crashes = self.crashes
            timeline = crashes.newest_values()
            if not len(timeline):
                result = None
            else:
                result = timeline[0]
            return result


    @property
    def events(self) -> PersiDict:
        with self.portal as portal:
            events_path = self + ["events"]
            events = portal.run_history.json.get_subdict(events_path)
            return events

    @property
    def last_event(self) -> Any:
        with self.portal as portal:
            events = self.events
            timeline = events.newest_values()
            if not len(timeline):
                result = None
            else:
                result = timeline[0]
            return result



class PureFnExecutionFrame(PortalAwareClass):
    session_id: str
    fn_address: PureFnExecutionResultAddr
    output_capturer = OutputCapturer
    exception_counter: int
    event_counter: int
    fn: PureFn

    def __init__(self, f_address: PureFnExecutionResultAddr):
        super().__init__(portal=f_address.portal)
        self.session_id = "run"+get_random_signature()
        self.fn_address = f_address
        self.fn = f_address.fn
        self.output_capturer = OutputCapturer()
        self.exception_counter = 0
        self.event_counter = 0
        self.context_used = False


    @property
    def portal(self) -> PureCodePortal:
        return super().portal

    def __enter__(self):
        assert self.context_used == False, (
            "An instance of PureFnExecutionFrame can be used only once.")
        self.context_used = True
        assert self.exception_counter == 0, (
            "An instance of PureFnExecutionFrame can be used only once.")
        assert self.event_counter == 0, (
            "An instance of PureFnExecutionFrame can be used only once.")
        self.portal.__enter__()
        self.output_capturer.__enter__()
        self.fn.call_stack.append(self)
        self.register_execution_attempt()
        return self

    def register_execution_attempt(self):
        execution_attempts = self.fn_address.execution_attempts
        attempt_id = self.session_id+"_a"
        execution_attempts[attempt_id] = build_execution_environment_summary()
        self.portal.run_history.py[self.fn_address + ["source"]] = (
            self.fn_address.fn_source_code)
        self.portal.run_history.py[
            self.fn_address + ["augmented_source"]] = (
            self.fn_address.function.augmented_fn_source_code)

    def register_execution_result(self, result: Any):
        self.portal.run_history.pkl[
            self.fn_address + ["results", self.session_id]] = result

    def __exit__(self, exc_type, exc_value, trace_back):
        self.output_capturer.__exit__(exc_type, exc_value, traceback)

        output_id = self.session_id+"_output"
        execution_outputs = self.fn_address.execution_outputs
        execution_outputs[output_id] = self.output_capturer.get_output()

        # self.register_exception(
        #     exc_type=exc_type, exc_value=exc_value, trace_back=trace_back)

        self.portal.__exit__(exc_type, exc_value, traceback)
        self.fn.call_stack.pop()


    def _extra_exception_data(self) -> dict:
        return dict(session_id = self.session_id)


    def register_exception(self
            , exception_id
            , data_to_persist) -> None:
        self.fn_address.crashes[exception_id] = data_to_persist
        self.exception_counter += 1

    def register_event(self, event_type:str|None, *args, **kwargs):
        # event_id = self.session_id + f"_e_{self.event_counter}"
        # if event_type is not None:
        #     event_id += "_"+ event_type
        # events = self.fn_address.events
        # events[event_id] = add_execution_environment_summary(
        #     *args, **kwargs, event_type=event_type)
        #
        # event_id = self.session_id + f"_e_{self.event_counter}"
        # if event_type is not None:
        #     kwargs["event_type"] = event_type
        #     event_id = event_type + "_"+ event_id
        # event_id = self.fn_address.island_name + "_" + event_id
        # event_id = self.fn_address.fn_name + "_" + event_id
        # DataPortal.register_event_globally(event_id, *args, **kwargs)

        self.event_counter += 1


# NEW GOOD
class PureFnExecutionRecord(PortalAwareClass):
    """ A record of an attempt to execute a pure function.

    It provides access to all information, logged during the
    execution attempt, which includes information about the execution context
    (environment), function arguments, its output (everything that was
    printed to stdout/stderr during the execution attempt), any crashes
    (exceptions) and events fired, and an actual result of the execution
    (created by a 'return' statement within the function code).
    """
    result_addr: PureFnExecutionResultAddr
    session_id: str
    def __init__(
            self
            , result_addr: PureFnExecutionResultAddr
            , session_id: str):
        super().__init__(portal=result_addr.portal)
        self.result_addr = result_addr
        self.session_id = session_id


    @property
    def portal(self) -> PureCodePortal:
        return super().portal

    @property
    def output(self) -> str|None:
        with self.portal:
            execution_outputs = self.result_addr.execution_outputs
            for k in execution_outputs:
                if self.session_id in k[-1]:
                    return execution_outputs[k]
            return None

    @property
    def attempt_context(self)-> dict|None:
        with self.portal:
            execution_attempts = self.result_addr.execution_attempts
            for k in execution_attempts:
                if self.session_id in k[-1]:
                    return execution_attempts[k]
            return None

    @property
    def crashes(self) -> list[dict]:
        result = []
        with self.portal:
            crashes = self.result_addr.crashes
            for k in crashes:
                if self.session_id in k[-1]:
                    result.append(crashes[k])
        return result

    @property
    def events(self) -> list[dict]:
        result = []
        with self.portal:
            events = self.result_addr.events
            for k in events:
                if self.session_id in k[-1]:
                    result.append(events[k])
        return result

    @property
    def result(self)->Any:
        with self.portal:
            execution_results = self.result_addr.execution_results
            for k in execution_results:
                if self.session_id in k[-1]:
                    return execution_results[k].get()
            assert False, "Result not found"

    @property
    def kwargs(self)-> dict:
        with self.portal:
            return self.result_addr.kwargs
