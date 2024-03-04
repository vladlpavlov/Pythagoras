from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)
from pythagoras._01_foundational_objects.value_addresses import ValueAddress
from pythagoras._03_autonomous_functions import *

import pytest

import pythagoras as pth


def test_load_save_error(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")
    assert len(pth.value_store) == 0
    def f(a, b):
        return a + b

    f_1 = AutonomousFunction(f, island_name="test")
    f_1_address = ValueAddress(f_1)
    assert len(pth.value_store) == 1
    del pth.all_autonomous_functions["test"]

    def f(a, b):
        return a * b * 2

    f_2 = AutonomousFunction(f, island_name="test")
    f_2_address = ValueAddress(f_2)
    assert len(pth.value_store) == 2
    del pth.all_autonomous_functions["test"]

    f_a = f_1_address.get()
    assert f_a(a=1, b=2) == 3

    with pytest.raises(Exception):
        f_b = f_2_address.get()