from __future__ import annotations

import time
import traceback
from copy import deepcopy
from typing import Callable, Any, List, TypeAlias
from sklearn.model_selection import ParameterGrid

from persidict import PersiDict

from pythagoras import DataPortal
from pythagoras._010_basic_portals.foundation import PortalAwareClass
from pythagoras._820_strings_signatures_converters.random_signatures import (
    get_random_signature)

from pythagoras._030_data_portals.hash_addresses import HashAddr
from pythagoras._030_data_portals.value_addresses import ValueAddr

from pythagoras.___03_OLD_autonomous_functions.autonomous_funcs import (
    AutonomousFn, register_autonomous_function, CodePortal)

from pythagoras._040_ordinary_functions.ordinary_funcs import (
    OrdinaryFn)

from pythagoras.___04_idempotent_functions.kw_args import SortedKwArgs
from pythagoras.___04_idempotent_functions.persidict_to_timeline import (
    build_timeline_from_persidict)
from pythagoras.___04_idempotent_functions.process_augmented_func_src import (
    process_augmented_func_src)
from pythagoras.___04_idempotent_functions.output_capturer import OutputCapturer
from pythagoras._020_logging_portals.execution_environment_summary import (
    build_execution_environment_summary, add_execution_environment_summary)
# from pythagoras._01_99_foundational_objects.global_event_loggers import (
#     register_exception_globally, register_event_globally)


ASupportingFunc:TypeAlias = str | AutonomousFn

SupportingFuncs:TypeAlias = ASupportingFunc | List[ASupportingFunc] | None



class IdempotentFn(AutonomousFn):
    augmented_code_checked: bool
    validators: SupportingFuncs
    correctors: SupportingFuncs
    def __init__(self, a_fn: Callable | str | OrdinaryFn
                 , island_name:str | None = None
                 , validators: SupportingFuncs = None
                 , correctors: SupportingFuncs = None
                 , portal: CodePortal|None = None):
        super().__init__(a_fn, island_name, portal = portal)
        if validators is None:
            assert correctors is None
        self.validators = self._process_supporting_functions_arg(validators)
        self.correctors = self._process_supporting_functions_arg(correctors)
        self.augmented_code_checked = False
        register_idempotent_function(self)


    def _process_supporting_functions_arg(
            self
            , supporting_funcs: SupportingFuncs = None
            ) -> List[str]|None:
        result = None
        if supporting_funcs is None:
            return result
        if isinstance(supporting_funcs, (AutonomousFn, str)):
            result = [supporting_funcs]
        else:
            result = supporting_funcs
        assert isinstance(result, list)
        result_names = []
        island = self.portal.all_autonomous_functions[self.island_name]
        for f in result:
            if isinstance(f, AutonomousFn):
                assert f.strictly_autonomous
                assert f.island_name == self.island_name
                assert f.portal == self.portal
                result_names.append(f.fn_name)
            else:
                assert isinstance(f, str)
                assert f in island
                result_names.append(f)
        reslut_names = sorted(result_names)
        return reslut_names


    def validate_environment(self):
        """Validate the environment before executing the function.

        This method is called before executing the function to
        validate if the current environment is suitable for execution.

        """
        if self.validators is not None:
            island = self.portal.all_autonomous_functions[self.island_name]
            for f in self.validators:
                island[f].execute()

    def correct_environment(self):
        """Correct the environment before executing the function.

        This method is called before executing the function to try to
        correct the environment to make it suitable for execution.
        """
        if self.correctors is not None:
            island = self.portal.all_autonomous_functions[self.island_name]
            for f in self.correctors:
                island[f].execute()


    @property
    def can_be_executed(self) -> bool:
        """Indicates if the function can be executed in the current environment.

        If the first validation attempt fails,
        it tries to correct the environment and then validates it again.

        If the second validation attempt fails, returns False.
        """
        with self.portal:

            try:
                self.validate_environment()
                return True
            except:
                pass

            try:
                self.correct_environment()
                self.validate_environment()
                return True
            except:
                pass

            return False


    @property
    def fn_type(self) -> str:
        return "idempotent"

    @property
    def decorator(self) -> str:
        decorator_str = "@pth.idempotent("
        decorator_str += f"\n\tisland_name='{self.island_name}'"
        if self.validators is not None:
            validators_str = f"\n\t, validators={self.validators}"
            decorator_str += validators_str
        if self.correctors is not None:
            correctors_str = f"\n\t, correctors={self.correctors}"
            decorator_str += correctors_str
        decorator_str += ")"
        return decorator_str

    def perform_runtime_checks(self):
        super().perform_runtime_checks()
        island_name = self.island_name
        island = self.portal.all_autonomous_functions[island_name]

        if not self.augmented_code_checked:
            augmented_code = ""

            full_dependencies = []
            if self.validators is not None:
                full_dependencies += self.validators
            if self.correctors is not None:
                full_dependencies += self.correctors
            full_dependencies += self.dependencies

            for fn_name in full_dependencies:
                f = island[fn_name]
                augmented_code += f.decorator + "\n"
                augmented_code += f.fn_source_code + "\n"
                augmented_code += "\n"

            name = self.fn_name
            if (not hasattr(island[name], "_augmented_source_code")
                or island[name]._augmented_source_code is None):
                island[name]._augmented_source_code = augmented_code
            else:
                assert island[name]._augmented_source_code == augmented_code

            self.augmented_code_checked = True

        return True


    @property
    def augmented_fn_source_code(self) -> str:
        """The augmented source code of the function.

        The augmented source code of an idempotent function
        includes the source code of the function itself,
        as well as the source code of all the autonomous functions
        it depends on, including validators and correctors.
        """

        island_name = self.island_name
        island = self.portal.all_autonomous_functions[island_name]
        assert hasattr(island[self.fn_name], "_augmented_source_code")
        assert island[self.fn_name]._augmented_source_code is not None
        assert self.augmented_code_checked
        return island[self.fn_name]._augmented_source_code


    def __getstate__(self):
        """Return the state of the object for pickling. """
        self.perform_runtime_checks()
        draft_state = dict(fn_name=self.fn_name
            , fn_source_code=self.fn_source_code
            , island_name=self.island_name
            , augmented_fn_source_code=self.augmented_fn_source_code
            , strictly_autonomous=self.strictly_autonomous
            , validators=self.validators
            , correctors=self.correctors
            , class_name=self.__class__.__name__)
        state = dict()
        for key in sorted(draft_state):
            state[key] = draft_state[key]
        return state

    def __setstate__(self, state):
        """Set the state of the object from a pickled state."""
        assert len(state) == 8
        assert state["class_name"] == IdempotentFn.__name__
        self.fn_name = state["fn_name"]
        self.fn_source_code = state["fn_source_code"]
        self.island_name = state["island_name"]
        self.strictly_autonomous = state["strictly_autonomous"]
        self.validators = state["validators"]
        self.correctors = state["correctors"]
        self.augmented_code_checked = False
        self._portal = None
        register_idempotent_function(self)

        with self.portal as portal:
            island_name = self.island_name
            island = self.portal.all_autonomous_functions[island_name]
            fn_name = self.fn_name
            if island[fn_name]._augmented_source_code is None:
                island[fn_name]._augmented_source_code = (
                    state["augmented_fn_source_code"])
                process_augmented_func_src(
                    state["augmented_fn_source_code"], portal=portal)
            else:
                assert state["augmented_fn_source_code"] == (
                    island[fn_name]._augmented_source_code)

        self.augmented_code_checked = True


    def get_address(self, **kwargs) -> IdempotentFnExecutionResultAddr:
        with self.portal:
            packed_kwargs = SortedKwArgs(**kwargs).pack(self.portal)
            result_address = IdempotentFnExecutionResultAddr(self, packed_kwargs)
            return result_address


    def swarm(self, **kwargs) -> IdempotentFnExecutionResultAddr:
        """ Request execution of the function with the given arguments.

        The function is executed in the background. The result can be
        retrieved later using the returned address.
        """
        with self.portal:
            result_address = self.get_address(**kwargs)
            result_address.request_execution()
            return result_address

    def run(self, **kwargs) -> IdempotentFnExecutionResultAddr:
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
            output_address = IdempotentFnExecutionResultAddr(self, packed_kwargs)
            _pth_f_addr_ = output_address
            if output_address.ready:
                return output_address.get()
            with IdempotentFnExecutionContext(output_address) as _pth_ec:
                output_address.request_execution()
                _pth_ec.register_execution_attempt()
                self.portal.run_history.py[output_address + ["source"]] = (
                    self.fn_source_code)
                self.portal.run_history.py[
                    output_address + ["augmented_source"]] = (
                    self.augmented_fn_source_code)
                assert output_address.can_be_executed
                unpacked_kwargs = SortedKwArgs(**packed_kwargs).unpack(portal)
                result = super().execute(**unpacked_kwargs)
                result_addr = ValueAddr(result)
                try: #TODO: refactor this
                    if output_address not in portal.execution_results:
                        portal.execution_results[output_address] = result_addr
                except:
                    pass
                finally:
                    assert output_address in portal.execution_results
                self.portal.run_history.pkl[
                    output_address + ["results",_pth_ec.session_id]] = result_addr
                output_address.drop_execution_request()
                return result

    def swarm_list(
            self
            , list_of_kwargs:list[dict]
            ) -> list[IdempotentFnExecutionResultAddr]:
        assert isinstance(list_of_kwargs, (list, tuple))
        for kwargs in list_of_kwargs:
            assert isinstance(kwargs, dict)
        with self.portal:
            addrs = []
            for kwargs in list_of_kwargs:
                new_addr = IdempotentFnExecutionResultAddr(self, kwargs)
                new_addr.request_execution()
                addrs.append(new_addr)
            return addrs

    def run_list(
            self
            , list_of_kwargs:list[dict]
            ) -> list[IdempotentFnExecutionResultAddr]:
        with self.portal:
            addrs = self.swarm_list(list_of_kwargs)
            addrs_workspace = deepcopy(addrs)
            self.portal.entropy_infuser.shuffle(addrs_workspace)
            for an_addr in addrs_workspace:
                an_addr.execute()
            return addrs

    def swarm_grid(
            self
            , grid_of_kwargs:dict[str, list] # refactor
            ) -> list[IdempotentFnExecutionResultAddr]:
        with self.portal:
            param_list = list(ParameterGrid(grid_of_kwargs))
            addrs = self.swarm_list(param_list)
            return addrs

    def run_grid(
            self
            , grid_of_kwargs:dict[str, list] # refactor
            ) -> list[IdempotentFnExecutionResultAddr]:
        with self.portal:
            param_list = list(ParameterGrid(grid_of_kwargs))
            addrs = self.run_list(param_list)
            return addrs



def register_idempotent_function(a_fn: IdempotentFn) -> None:
    """Register an idempotent function in the Pythagoras system."""
    assert isinstance(a_fn, IdempotentFn)
    register_autonomous_function(a_fn)
    island_name = a_fn.island_name
    island = a_fn.portal.all_autonomous_functions[island_name]
    name = a_fn.fn_name
    if not hasattr(island[name], "_augmented_source_code"):
        island[name]._augmented_source_code = None


class IdempotentFnCallSignature(PortalAwareClass):
    """A signature of a call to an idempotent function.

    This class is used to create a unique identifier for a call to an
    idempotent function. The identifier is used to store the result of the
    call in the value store.

    This is a supporting class for PureFnExecutionResultAddr.
    Pythagoras' users should not need to interact with it directly.
    """
    def __init__(self, a_fn:IdempotentFn, arguments:SortedKwArgs):
        portal = a_fn.portal
        super().__init__(portal= portal)
        assert isinstance(a_fn, IdempotentFn)
        assert isinstance(arguments, SortedKwArgs)
        self.fn_name = a_fn.fn_name
        self.fn_addr = ValueAddr(a_fn)
        self.args_addr = ValueAddr(arguments.pack(portal))

    def __getstate__(self):
        state = dict(
            fn_name=self.fn_name
            , fn_addr=self.fn_addr
            , args_addr=self.args_addr)
        return state

    def __setstate__(self, state):
        assert len(state) == 3
        self.fn_name = state["fn_name"]
        self.fn_addr = state["fn_addr"]
        self.args_addr = state["args_addr"]
        self._portal = None
        self.capture_portal()


    @property
    def portal(self) -> CodePortal:
        return super().portal


class IdempotentFnExecutionResultAddr(HashAddr):
    """An address of the result of an execution of an idempotent function.

    This class is used to point to the result of an execution of an idempotent
    function in a portal. The address is used to request an execution and
    to retrieve the result (if available) from the portal.

    The address also provides access to various logs and records of the
    function execution, such as environmental contexts of the execution attempts,
    outputs printed, exceptions thrown and events emitted.
    """

    def __init__(self, a_fn: IdempotentFn, arguments:dict[str, Any]):
        assert isinstance(a_fn, IdempotentFn)
        self._arguments = SortedKwArgs(**arguments)
        signature = IdempotentFnCallSignature(a_fn, self._arguments)
        tmp = ValueAddr(signature)
        new_prefix = a_fn.fn_name
        if a_fn.island_name is not None:
            new_prefix += "_" + a_fn.island_name
        new_hash_value = tmp.hash_value
        super().__init__(new_prefix, new_hash_value, portal=a_fn.portal)
        self._function = a_fn

    @property
    def portal(self) -> CodePortal:
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
                prefix="idempotentfncallsignature"
                , hash_value=self.hash_value
                , portal= portal)

    def __setstate__(self, state):
        assert len(state) == 1
        self.str_chain = state["str_chain"]
        self._portal = None
        self._invalidate_cache()
        self.capture_portal()


    def __getstate__(self):
        state = dict(str_chain=self.str_chain)
        return state

    @property
    def ready(self):
        """Indicates if the result of the function call is available."""
        if hasattr(self, "_ready"):
            return True
        with self.portal:
            result = (self in self.portal.execution_results)
            if result:
                self._ready = True
            return result

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
        if hasattr(self, "_result"):
            return self._result

        with self.portal as portal:

            if self.ready:
                result_addr = portal.execution_results[self]
                self._result = portal.value_store[result_addr]
                return self._result

            self.request_execution()

            start_time, backoff_period = time.time(), 1.0
            stop_time = (start_time + timeout) if timeout else None
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
    def function(self) -> IdempotentFn:
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
    def fn(self) -> IdempotentFn:
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
            return self.arguments.unpack(portal)


    @property
    def can_be_executed(self) -> bool:
        """Indicates if the function can be executed in the current session.

        The function should fe refactored once we start fully supporting
        VALIDATORS, CORRECTORS and SEQUENCERS
        """
        with self.portal:
            return self.function.can_be_executed


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
                past_attempts.mtimestamp(a) for a in past_attempts)
            current_timestamp = time.time()
            if (current_timestamp - most_recent_timestamp
                    > DEFAULT_EXECUTION_TIME*(2**n_past_attempts)):
                return True
            return False



    @property
    def execution_records(self) -> list[IdempotentFnExecutionRecord]:
        with self.portal:
            result = []
            for k in self.execution_attempts:
                run_id = k[-1][:-2]
                result.append(IdempotentFnExecutionRecord(self,run_id))
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
            timeline = build_timeline_from_persidict(attempts)
            if not len(timeline):
                result = None
            else:
                result = timeline[-1]
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
            timeline = build_timeline_from_persidict(outputs)
            if not len(timeline):
                result = None
            else:
                result = timeline[-1]
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
            timeline = build_timeline_from_persidict(crashes)
            if not len(timeline):
                result = None
            else:
                result = timeline[-1]
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
            timeline = build_timeline_from_persidict(events)
            if not len(timeline):
                result = None
            else:
                result = timeline[-1]
            return result


class IdempotentFnExecutionContext(PortalAwareClass):
    session_id: str
    fn_address: IdempotentFnExecutionResultAddr
    output_capturer = OutputCapturer
    exception_counter: int
    event_counter: int

    def __init__(self, f_address: IdempotentFnExecutionResultAddr):
        super().__init__(portal=f_address.portal)
        self.session_id = get_random_signature()
        self.fn_address = f_address
        self.output_capturer = OutputCapturer()
        self.exception_counter = 0
        self.event_counter = 0


    @property
    def portal(self) -> CodePortal:
        return super()._portal

    def __enter__(self):
        self.portal.__enter__()
        self.output_capturer.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, trace_back):
        self.output_capturer.__exit__(exc_type, exc_value, traceback)

        output_id = self.session_id+"_o"
        execution_outputs = self.fn_address.execution_outputs
        execution_outputs[output_id] = self.output_capturer.get_output()

        self.register_exception(
            exc_type=exc_type, exc_value=exc_value, trace_back=trace_back)

        self.portal.__exit__(exc_type, exc_value, traceback)



    def register_execution_attempt(self):
        execution_attempts = self.fn_address.execution_attempts
        attempt_id = self.session_id+"_a"
        execution_attempts[attempt_id] = build_execution_environment_summary()


    def register_exception(self,exc_type, exc_value, trace_back, **kwargs):
        if exc_value is None:
            return
        exception_id = self.session_id + f"_c_{self.exception_counter}"
        self.fn_address.crashes[exception_id] = add_execution_environment_summary(
            **kwargs, exc_value=exc_value)
        self.exception_counter += 1
        exception_id = exc_type.__name__ + "_"+ exception_id
        exception_id = self.fn_address.island_name + "_" + exception_id
        exception_id = self.fn_address.fn_name + "_" + exception_id
        DataPortal.register_exception_globally(**kwargs, exception_id=exception_id)

    def register_event(self, event_type:str|None, *args, **kwargs):
        event_id = self.session_id + f"_e_{self.event_counter}"
        if event_type is not None:
            event_id += "_"+ event_type
        events = self.fn_address.events
        events[event_id] = add_execution_environment_summary(
            *args, **kwargs, event_type=event_type)

        event_id = self.session_id + f"_e_{self.event_counter}"
        if event_type is not None:
            kwargs["event_type"] = event_type
            event_id = event_type + "_"+ event_id
        event_id = self.fn_address.island_name + "_" + event_id
        event_id = self.fn_address.fn_name + "_" + event_id
        DataPortal.register_event_globally(event_id, *args, **kwargs)

        self.event_counter += 1


class IdempotentFnExecutionRecord(PortalAwareClass):
    """ A record of an attempt to execute an idempotent function.

    It provides access to all information, persisted
    during the execution attempt, which includes information about
    the execution context (environment), function arguments,
    its output (everything that was printed to stdout/stderr
    during the execution attempt), any crashes (exceptions) and events fired,
    and an actual result of the execution (created by a 'return' statement
    within the function code).
    """
    result_addr: IdempotentFnExecutionResultAddr
    session_id: str
    def __init__(
            self
            , result_addr: IdempotentFnExecutionResultAddr
            , session_id: str):
        super().__init__(portal=result_addr.portal)
        self.result_addr = result_addr
        self.session_id = session_id


    @property
    def portal(self) -> CodePortal:
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
        with self.portal:
            result = []
            crashes = self.result_addr.crashes
            for k in crashes:
                if self.session_id in k[-1]:
                    result.append(crashes[k])
            return result

    @property
    def events(self) -> list[dict]:
        with self.portal:
            result = []
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
