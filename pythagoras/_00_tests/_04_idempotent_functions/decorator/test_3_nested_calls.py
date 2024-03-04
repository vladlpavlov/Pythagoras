import pytest

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)


def a():
    return 2

def b():
    return a()*2

def c():
    return b()*2

def test_2_nested_calls(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    global a, b, c

    assert not is_idempotent(a)
    assert not is_idempotent(b)
    assert not is_idempotent(c)

    assert a() == 2
    assert b() == 4
    assert c() == 8


    c = idempotent()(c)
    a = idempotent()(a)
    b = idempotent()(b)

    assert is_idempotent(a)
    assert is_idempotent(b)
    assert is_idempotent(c)

    assert c() == 8