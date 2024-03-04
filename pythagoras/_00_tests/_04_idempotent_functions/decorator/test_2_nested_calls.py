import pytest

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)


def f_nstd():
    return 5

def g_nstd():
    return f_nstd()

def test_2_nested_calls(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    global f_nstd, g_nstd

    assert not is_idempotent(f_nstd)
    assert not is_idempotent(g_nstd)
    assert g_nstd() == 5
    g_nstd = idempotent()(g_nstd)
    f_nstd = idempotent()(f_nstd)

    assert is_idempotent(f_nstd)
    assert is_idempotent(g_nstd)
    assert g_nstd() == 5