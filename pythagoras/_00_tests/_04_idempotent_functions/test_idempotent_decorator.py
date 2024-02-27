import pytest

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._05_mission_control.global_state_management import (
    _clean_global_state, initialize)


def test_basics(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)
    def f_ab(a, b):
        return a + b

    result = f_ab(a=1,b=2)
    assert not is_idempotent(f_ab)
    f_1 = idempotent()(f_ab)
    #
    assert is_idempotent(f_1)
    assert f_1(a=1,b=2) == result

def test_init_checks(tmpdir):
    _clean_global_state()
    def f():
        pass

    with pytest.raises(AssertionError):
        idempotent()(f)

    _clean_global_state()
    initialize(base_dir=tmpdir)

    idempotent()(f)

def f_nstd():
    return 5

def g_nstd():
    return f_nstd()

def test_nested_calls(tmpdir):
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