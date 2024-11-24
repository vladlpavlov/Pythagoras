import pytest
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)
from pythagoras.___04_idempotent_functions.process_augmented_func_src import (
    process_augmented_func_src)
import pythagoras as pth

src_1_good ="""
@pth.autonomous()
def f_1():
    pass
"""

src_2_good ="""
@pth.autonomous() # this is a decorator
def f_1(): # this is a function named f_1
    'a docstring'
    pass # this statement does nothing
"""



def test_basic_func_registration(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):

        assert len(pth.all_autonomous_functions) == 1

        for _ in range(2):
            process_augmented_func_src(src_1_good)
            assert len(pth.all_autonomous_functions) == 1
            assert len(pth.all_autonomous_functions[pth.default_island_name]) == 1

            process_augmented_func_src(src_2_good)
            assert len(pth.all_autonomous_functions) == 1
            assert len(pth.all_autonomous_functions[pth.default_portal.default_island_name]) == 1
