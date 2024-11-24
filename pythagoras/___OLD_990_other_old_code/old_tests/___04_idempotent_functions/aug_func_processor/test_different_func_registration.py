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

src_2_bad ="""
@pth.autonomous() # this is a decorator
def f_1(): 
    print()
"""



def test_basic_func_registration(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):

        assert len(pth.default_portal.all_autonomous_functions) == 1

        process_augmented_func_src(src_1_good)
        process_augmented_func_src(src_1_good)
        assert len(pth.default_portal.all_autonomous_functions) == 1
        assert len(pth.default_portal.all_autonomous_functions[pth.default_island_name]) == 1

        with pytest.raises(Exception):
            process_augmented_func_src(src_2_bad)