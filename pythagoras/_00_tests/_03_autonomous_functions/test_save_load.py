from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)
from pythagoras._01_foundational_objects.value_addresses import ValueAddress
from pythagoras._03_autonomous_functions import *

import pytest

import pythagoras as pth

def test_load_save(tmpdir):
    with initialize(
            base_dir=tmpdir
            , default_island_name="test"
            , cloud_type="local"
            , n_background_workers=0):

        def f(a, b):
            return a + b

        f_1 = AutonomousFunction(f, island_name="test")
        f_address = ValueAddress(f_1)

        f_2 = f_address.get()
        assert f_2(a=1, b=2) == f(a=1, b=2) == 3
        assert f_2.name == f_1.name
        assert f_2.naked_source_code == f_1.naked_source_code
        assert f_2.island_name == f_1.island_name

        del pth.all_autonomous_functions["test"]

        f_3 = f_address.get()
        assert f_3(a=1, b=2) == f(a=1, b=2) == 3
        assert f_3.name == "f"
        assert f_3.island_name == "test"