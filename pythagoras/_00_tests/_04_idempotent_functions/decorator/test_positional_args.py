import pytest

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)


def bad_f(*args):
    return args[0]

def good_f(a):
    return a

def test_positional_args(tmpdir):
    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)

    global bad_f, good_f

    with pytest.raises(Exception):
        bad_f = idempotent()(bad_f)

    good_f = idempotent()(good_f)

    assert good_f(a=10) == 10
    with pytest.raises(Exception):
        good_f(10)
