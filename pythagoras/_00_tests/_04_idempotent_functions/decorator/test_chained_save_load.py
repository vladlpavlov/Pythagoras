import pytest

from pythagoras._01_foundational_objects.value_addresses import ValueAddress

from pythagoras._04_idempotent_functions.idempotent_decorator import (
    idempotent)
from pythagoras._07_mission_control.global_state_management import (
    _force_initialize)

import pythagoras as pth


def f1():
    return 0

def f2():
    return f1()*2

def f3():
    return f2()*3

def f4():
    return f3()*4

def test_chained_save_load(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):

        global f1, f2, f3, f4

        f1 = idempotent()(f1)
        f2 = idempotent()(f2)
        f3 = idempotent()(f3)

        assert f3() == 0
        assert f4() == 0

        address_3 = ValueAddress(f3)
        assert address_3.get()() == 0

    address_3._invalidate_cache()

    with _force_initialize(tmpdir, n_background_workers=0):
        del f1, f2, f3, f4

        new_f3 = address_3.get()
        result = new_f3()
        assert result == 0
