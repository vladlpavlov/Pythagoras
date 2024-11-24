
from pythagoras.___04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras.___04_idempotent_functions.idempotent_func_address_context import (
    IdempotentFnExecutionResultAddr)
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)


def factorial(n:int) -> int:
    if n in [0, 1]:
        return 1
    else:
        return n * factorial(n=n-1)

def test_needs_execution(tmpdir):

    with _force_initialize(tmpdir, n_background_workers=0):
    # initialize(base_dir="TTTTTTTTTTTTTTTTTTTTT")

        global factorial
        factorial = idempotent()(factorial)

        addr = IdempotentFnExecutionResultAddr(a_fn=factorial, arguments=dict(n=5))

        assert not addr.ready
        assert addr.can_be_executed
        assert addr.needs_execution
        assert len(addr.execution_attempts) == 0
        addr.request_execution()
        assert addr.execution_requested

        factorial(n=5)
        assert addr.ready
        assert addr.can_be_executed
        assert not addr.needs_execution
        assert len(addr.execution_attempts) == 1
        assert not addr.execution_requested





