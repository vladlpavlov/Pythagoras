import pytest
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)
from pythagoras._04_idempotent_functions.process_augmented_func_src import (
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
    _clean_global_state()
    initialize(tmpdir)

    assert len(pth.all_autonomous_functions) == 2
    assert len(pth.all_autonomous_functions[None]) == 0


    process_augmented_func_src(src_1_good)
    assert len(pth.all_autonomous_functions) == 2
    assert len(pth.all_autonomous_functions[None]) == 0
    assert len(pth.all_autonomous_functions[pth.default_island_name]) == 1

    with pytest.raises(Exception):
        process_augmented_func_src(src_2_bad)