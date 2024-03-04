import pytest

from persidict import FileDirDict

from pythagoras._02_ordinary_functions.ordinary_decorator import ordinary
from pythagoras._03_autonomous_functions.autonomous_decorators import autonomous
from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._04_idempotent_functions.idempotent_func_and_address import (
    FuncOutputAddress)
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth



def test_execution_attempts_simple(tmpdir):

    _clean_global_state()
    initialize(base_dir=tmpdir)


    @idempotent()
    def simple_func()->int:
        return 10

    assert len(pth.function_execution_attempts) == 0
    assert simple_func() == 10
    assert len(pth.function_execution_attempts) == 1
    assert len(FuncOutputAddress(simple_func, dict()).execution_attempts) == 1
    assert len(simple_func.execution_attempts()) == 1


def test_execution_attempts_weird(tmpdir):

    _clean_global_state()
    initialize(base_dir=tmpdir)


    @idempotent()
    def weird_func()->int:
        import pythagoras as pth
        if len(pth.function_execution_attempts) < 3:
            return 10/0
        return 10

    assert len(pth.function_execution_attempts) == 0

    with pytest.raises(ZeroDivisionError):
        weird_func()
    assert len(pth.function_execution_attempts) == 1
    assert len(FuncOutputAddress(weird_func, dict()).execution_attempts) == 1
    assert len(weird_func.execution_attempts()) == 1
    assert len(pth.global_crash_history) == 1
    assert len(pth.function_execution_requests) == 1
    assert len(pth.function_output_store) == 0

    with pytest.raises(ZeroDivisionError):
        weird_func()
    assert len(pth.function_execution_attempts) == 2
    assert len(FuncOutputAddress(weird_func, dict()).execution_attempts) == 2
    assert len(weird_func.execution_attempts()) == 2
    assert len(pth.global_crash_history) == 2
    assert len(pth.function_execution_requests) == 1
    assert len(pth.function_output_store) == 0

    assert weird_func() == 10
    assert len(pth.function_execution_attempts) == 3
    assert len(FuncOutputAddress(weird_func, dict()).execution_attempts) == 3
    assert len(weird_func.execution_attempts()) == 3
    assert len(pth.global_crash_history) == 2
    assert len(pth.function_execution_requests) == 0
    assert len(pth.function_output_store) == 1

