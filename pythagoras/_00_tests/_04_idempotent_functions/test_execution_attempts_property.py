import pytest

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth


def test_execution_attempts_simple(tmpdir):

    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)


    @idempotent()
    def simple_func()->int:
        return 10

    assert len(simple_func.get_address().execution_attempts) == 0
    assert simple_func() == 10
    assert len(simple_func.get_address().execution_attempts) == 1



def test_execution_attempts_weird(tmpdir):

    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)


    @idempotent()
    def weird_func()->int:
        import pythagoras as pth
        if len(pth.all_autonomous_functions[pth.default_island_name]
               ["weird_func"].get_address().execution_attempts) < 3:
            return 10/0
        return 10

    assert len(weird_func.get_address().execution_attempts) == 0

    with pytest.raises(ZeroDivisionError):
        weird_func()
    assert len(weird_func.get_address().execution_attempts) == 1
    assert len(pth.crash_history) == 1
    assert len(pth.run_history.binary) == 1
    assert len(pth.execution_results) == 0

    with pytest.raises(ZeroDivisionError):
        weird_func()
    assert len(weird_func.get_address().execution_attempts) == 2
    assert len(pth.crash_history) == 2
    assert len(pth.run_history.binary) == 1
    assert len(pth.execution_results) == 0

    assert weird_func() == 10
    assert len(weird_func.get_address().execution_attempts) == 3
    assert len(pth.crash_history) == 2
    assert len(pth.run_history.binary) == 0
    assert len(pth.execution_results) == 1