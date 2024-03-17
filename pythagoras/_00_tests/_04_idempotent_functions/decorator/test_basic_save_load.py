import pytest

from pythagoras._01_foundational_objects.value_addresses import ValueAddr

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth


def my_function():
    return 2024

def test_basic_save_load(tmpdir):
    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)

    global my_function

    my_function = idempotent()(my_function)

    assert my_function() == 2024

    address = None
    # assert len(pth.value_store) == 0
    for i in range(3): address = ValueAddr(my_function)
    for i in range(3): assert address.get()() == 2024
    # assert len(pth.value_store) == 1