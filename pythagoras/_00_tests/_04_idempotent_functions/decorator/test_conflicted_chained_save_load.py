import pytest

from pythagoras._01_foundational_objects.value_addresses import ValueAddress

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth


def f1():
    return 0

def f2():
    return f1()*2

def f3():
    return f2()*3

def f4():
    return f3()*4

def test_conflicted_chained_save_load(tmpdir):
    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)

    global f1, f2, f3, f4

    f1 = idempotent()(f1)
    f2 = idempotent()(f2)
    f3 = idempotent()(f3)
    f4 = idempotent()(f4)

    assert f3() == 0
    assert f4() == 0

    address_2 = ValueAddress(f2)
    address_4 = ValueAddress(f4)

    assert address_2.get()() == 0
    assert address_4.get()() == 0

    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)
    del f1, f2, f3, f4

    @idempotent()
    def f3():
        return 2024

    assert address_2.get()() == 0

    with pytest.raises(Exception):
        address_4.get()

