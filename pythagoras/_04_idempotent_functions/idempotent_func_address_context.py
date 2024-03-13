from __future__ import annotations

import time
import traceback
from typing import Callable, Any

from persidict import PersiDict

import pythagoras as pth
from pythagoras._01_foundational_objects.hash_and_random_signatures import (
    get_random_signature)

from pythagoras._01_foundational_objects.hash_addresses import HashAddress
from pythagoras._01_foundational_objects.value_addresses import ValueAddress

from pythagoras._03_autonomous_functions.autonomous_funcs import (
    AutonomousFunction, register_autonomous_function)

from pythagoras._02_ordinary_functions.ordinary_funcs import (
    OrdinaryFunction)

from pythagoras._04_idempotent_functions.kw_args import (
    UnpackedKwArgs, PackedKwArgs, SortedKwArgs)
from pythagoras._04_idempotent_functions.process_augmented_func_src import (
    process_augmented_func_src)
from pythagoras._04_idempotent_functions.output_capturer import OutputCapturer
from pythagoras._05_events_and_exceptions.execution_environment_summary import (
    build_execution_environment_summary, add_execution_environment_summary)
from pythagoras._05_events_and_exceptions.global_event_loggers import (
    register_exception_globally, register_event_globally)


class IdempotentFunction(AutonomousFunction):
    augmented_code_checked: bool
    def __init__(self, a_func: Callable | str | OrdinaryFunction
            , island_name:str | None = None):
        super().__init__(a_func, island_name)
        self.augmented_code_checked = False
        register_idempotent_function(self)

    @property
    def decorator(self) -> str:
        decorator_str = "@pth.idempotent("
        decorator_str += f"island_name='{self.island_name}'"
        decorator_str += ")"
        return decorator_str

    def runtime_checks(self):
        super().runtime_checks()
        island_name = self.island_name
        island = pth.all_autonomous_functions[island_name]

        if not self.augmented_code_checked:
            augmented_code = ""
            for f_name in self.dependencies:
                f = island[f_name]
                augmented_code += f.decorator + "\n"
                augmented_code += f.naked_source_code + "\n"
                augmented_code += "\n"

            name = self.name
            if (not hasattr(island[name], "_augmented_source_code")
                or island[name]._augmented_source_code is None):
                island[name]._augmented_source_code = augmented_code
            else:
                assert island[name]._augmented_source_code == augmented_code

            self.augmented_code_checked = True

        return True


    @property
    def augmented_source_code(self) -> str:
        island_name = self.island_name
        island = pth.all_autonomous_functions[island_name]
        assert hasattr(island[self.name], "_augmented_source_code")
        assert island[self.name]._augmented_source_code is not None
        assert self.augmented_code_checked
        return island[self.name]._augmented_source_code


    def __getstate__(self):
        assert self.runtime_checks()
        draft_state = dict(name=self.name
            , naked_source_code=self.naked_source_code
            , island_name=self.island_name
            , augmented_source_code=self.augmented_source_code
            , strictly_autonomous=self.strictly_autonomous
            , class_name=self.__class__.__name__)
        state = dict()
        for key in sorted(draft_state):
            state[key] = draft_state[key]
        return state

    def __setstate__(self, state):
        assert len(state) == 6
        assert state["class_name"] == IdempotentFunction.__name__
        self.name = state["name"]
        self.naked_source_code = state["naked_source_code"]
        self.island_name = state["island_name"]
        self.strictly_autonomous = state["strictly_autonomous"]
        self.augmented_code_checked = False
        register_idempotent_function(self)

        island_name = self.island_name
        island = pth.all_autonomous_functions[island_name]
        name = self.name
        if island[name]._augmented_source_code is None:
            island[name]._augmented_source_code = state["augmented_source_code"]
            process_augmented_func_src(state["augmented_source_code"])
        else:
            assert state["augmented_source_code"] == (
                island[name]._augmented_source_code)

        self.augmented_code_checked = True

    def get_address(self, **kwargs) -> FunctionExecutionResultAddress:
        packed_kwargs = PackedKwArgs(**kwargs)
        result_address = FunctionExecutionResultAddress(self, packed_kwargs)
        return result_address

    def swarm(self, **kwargs) -> FunctionExecutionResultAddress:
        result_address = self.get_address(**kwargs)
        result_address.request_execution()
        return result_address


    def execute(self, **kwargs) -> Any:
        packed_kwargs = PackedKwArgs(**kwargs)
        output_address = FunctionExecutionResultAddress(self, packed_kwargs)
        _pth_f_addr_ = output_address
        if output_address.ready:
            return output_address.get()
        with FunctionExecutionContext(output_address) as _pth_ec:
            output_address.request_execution()
            _pth_ec.register_execution_attempt()
            pth.run_history.py[output_address + ["source"]] = (
                self.naked_source_code)
            pth.run_history.py[
                output_address + ["augmented_source"]] = (
                self.augmented_source_code)
            unpacked_kwargs = UnpackedKwArgs(**packed_kwargs)
            result = super().execute(**unpacked_kwargs)
            pth.execution_results[output_address] = ValueAddress(result)
            output_address.drop_execution_request()
            return result

    def list_execute(self, list_of_kwargs:list[dict]) -> Any:
        assert isinstance(list_of_kwargs, (list, tuple))
        for kwargs in list_of_kwargs:
            assert isinstance(kwargs, dict)
        addrs = []
        for kwargs in list_of_kwargs:
            new_addr = FunctionExecutionResultAddress(self, kwargs)
            new_addr.request_execution()
            addrs.append(new_addr)
        addrs_indexed = list(zip(range(len(addrs)), addrs))
        pth.entropy_infuser.shuffle(addrs_indexed)
        results_dict = dict()
        for n, an_addr in addrs_indexed:
            results_dict[n] = an_addr.function.execute(**an_addr.arguments)
        results_list = [results_dict[n] for n in range(len(addrs))]
        return results_list


def register_idempotent_function(f: IdempotentFunction) -> None:
    """Register an idempotent function in the Pythagoras system."""
    assert isinstance(f, IdempotentFunction)
    register_autonomous_function(f)
    island_name = f.island_name
    island = pth.all_autonomous_functions[island_name]
    name = f.name
    if not hasattr(island[name], "_augmented_source_code"):
        island[name]._augmented_source_code = None


class FunctionCallSignature:
    def __init__(self,f:IdempotentFunction,arguments:SortedKwArgs):
        assert isinstance(f, IdempotentFunction)
        assert isinstance(arguments, SortedKwArgs)
        self.f_name = f.name
        self.f_addr = ValueAddress(f)
        self.args_addr = ValueAddress(arguments.pack())

class FunctionExecutionResultAddress(HashAddress):
    def __init__(self, f: IdempotentFunction, arguments:dict[str, Any]):
        assert isinstance(f, IdempotentFunction)
        arguments = SortedKwArgs(**arguments)
        signature = FunctionCallSignature(f,arguments)
        tmp = ValueAddress(signature)
        new_prefix = f.f_name
        if f.island_name is not None:
            new_prefix += "_" + f.island_name
        new_hash_value = tmp.hash_value
        super().__init__(new_prefix, new_hash_value)

    def get_ValueAddress(self):
        return ValueAddress.from_strings(  # TODO: refactor this
            prefix="functioncallsignature", hash_value=self.hash_value)

    @property
    def ready(self):
        result =  self in pth.execution_results
        return result

    def execute(self):
        function = self.function
        arguments = self.arguments
        result = function.execute(**arguments)
        return result

    def request_execution(self):
        if self in pth.execution_results:
            pth.execution_requests.delete_if_exists(self)
        else:
            if self not in pth.execution_requests:
                pth.execution_requests[self] = True

    def drop_execution_request(self):
        pth.execution_requests.delete_if_exists(self)

    def is_execution_requested(self):
        return self in pth.execution_requests

    def get(self, timeout: int = None):
        """Retrieve value, referenced by the address.

        If the value is not immediately available, backoff exponentially
        till timeout is exceeded. If timeout is None, keep trying forever.
        """
        if self.ready:
            return pth.value_store[pth.execution_results[self]]
        self.request_execution()

        start_time, backoff_period = time.time(), 1.0
        stop_time = (start_time + timeout) if timeout else None
        # start_time, stop_time and backoff_period are in seconds

        while True:
            if self.ready:
                result = pth.value_store[pth.execution_results[self]]
                self.drop_execution_request()
                return result
            else:
                time.sleep(backoff_period)
                backoff_period *= 2.0
                backoff_period += pth.entropy_infuser.uniform(-0.5, 0.5)
                if stop_time:
                    current_time = time.time()
                    if current_time + backoff_period > stop_time:
                        backoff_period = stop_time - current_time
                    if current_time > stop_time:
                        raise TimeoutError
                backoff_period = max(1.0, backoff_period)

    @property
    def function(self) -> IdempotentFunction:
        signature_addr = self.get_ValueAddress()
        signature = signature_addr.get()
        return signature.f_addr.get()

    @property
    def f_name(self) -> str:
        signature_addr = self.get_ValueAddress()
        signature = signature_addr.get()
        return signature.f_name

    @property
    def island_name(self) -> str:
        return self.function.island_name

    @property
    def arguments(self) -> SortedKwArgs:
        signature_addr = self.get_ValueAddress()
        signature = signature_addr.get()
        return signature.args_addr.get()

    @property
    def can_be_executed(self) -> bool:
        """Indicates if the function can be executed in the current session.

        Currently, it's just a placeholder that always returns True.

        The function should fe refactored once we start supporting
        VALIDATORS, CORRECTORS and SEQUENCERS
        """
        return True

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
    def execution_attempts(self) -> PersiDict:
        attempts_path = self + ["attempts"]
        attempts = pth.run_history.json.get_subdict(attempts_path)
        return attempts

    @property
    def execution_outputs(self) -> PersiDict:
        outputs_path = self + ["outputs"]
        outputs = pth.run_history.txt.get_subdict(outputs_path)
        return outputs

    @property
    def crashes(self) -> PersiDict:
        crashes_path = self + ["crashes"]
        crashes = pth.run_history.json.get_subdict(crashes_path)
        return crashes

    @property
    def events(self) -> PersiDict:
        events_path = self + ["events"]
        events = pth.run_history.json.get_subdict(events_path)
        return events

class FunctionExecutionContext:
    session_id: str
    f_address: FunctionExecutionResultAddress
    output_capturer = OutputCapturer
    exception_counter: int
    event_counter: int

    def __init__(self, f_address: FunctionExecutionResultAddress):
        self.session_id = get_random_signature()
        self.f_address = f_address
        self.output_capturer = OutputCapturer()
        self.exception_counter = 0
        self.event_counter = 0

    def __enter__(self):
        self.output_capturer.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, trace_back):
        self.output_capturer.__exit__(exc_type, exc_value, traceback)

        output_id = self.session_id+"_o"
        execution_outputs = self.f_address.execution_outputs
        execution_outputs[output_id] = self.output_capturer.get_output()

        self.register_exception(
            exc_type=exc_type, exc_value=exc_value, trace_back=trace_back)


    def register_execution_attempt(self):
        execution_attempts = self.f_address.execution_attempts
        attempt_id = self.session_id+"_a"
        execution_attempts[attempt_id] = build_execution_environment_summary()


    def register_exception(self,exc_type, exc_value, trace_back, **kwargs):
        if exc_value is None:
            return
        exception_id = self.session_id + f"_c_{self.exception_counter}"
        self.f_address.crashes[exception_id] = add_execution_environment_summary(
            **kwargs, exc_value=exc_value)
        self.exception_counter += 1
        exception_id = exc_type.__name__ + "_"+ exception_id
        exception_id = self.f_address.island_name + "_" + exception_id
        exception_id = self.f_address.f_name + "_" + exception_id
        register_exception_globally(**kwargs, exception_id=exception_id)

    def register_event(self, event_type:str|None=None, **kwargs):
        event_id = self.session_id + f"_e_{self.event_counter}"
        if event_type is not None:
            event_id += "_"+ event_type
        events = self.f_address.events
        events[event_id] = add_execution_environment_summary(**kwargs, event_type=event_type)

        event_id = self.session_id + f"_e_{self.event_counter}"
        if event_type is not None:
            kwargs["event_type"] = event_type
            event_id = event_type + "_"+ event_id
        event_id = self.f_address.island_name + "_" + event_id
        event_id = self.f_address.f_name + "_" + event_id
        register_event_globally(**kwargs, event_id=event_id)

        self.event_counter += 1