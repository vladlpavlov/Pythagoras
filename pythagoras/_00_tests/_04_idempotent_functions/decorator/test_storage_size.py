import pytest

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth



def test_no_args(tmpdir):

    _clean_global_state()
    initialize(base_dir=tmpdir)

    assert len(pth.value_store) == 0
    @idempotent()
    def f():
        return 0

    assert f() == 0
    assert len(pth.execution_results) == 1
    assert len(pth.value_store) == 4

def test_two_args(tmpdir):

    _clean_global_state()
    initialize(base_dir=tmpdir)

    assert len(pth.value_store) == 0

    @idempotent()
    def f_sum(x,y):
        return x+y

    assert f_sum(x=0,y=0) == 0
    assert len(pth.execution_results) == 1
    assert len(pth.value_store) == 4

    assert f_sum(x=2, y=3) == 5
    assert len(pth.execution_results) == 2
    assert len(pth.value_store) == 9