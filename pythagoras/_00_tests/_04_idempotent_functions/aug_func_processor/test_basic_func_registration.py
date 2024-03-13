import pytest
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)
from pythagoras._04_idempotent_functions.process_augmented_func_src import (
    process_augmented_func_src)
import pythagoras as pth

src_1_good ="""
@pth.autonomous(island_name='DEMO')
def f_1_1():
    pass
    
@pth.autonomous()
def f_1_2():
    pass
"""

def test_basic_func_registration(tmpdir):
    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)
    assert len(pth.all_autonomous_functions) == 1

    for _ in range(5):
        process_augmented_func_src(src_1_good)
        assert len(pth.all_autonomous_functions) == 2
        assert len(pth.all_autonomous_functions["DEMO"]) == 1
        assert len(pth.all_autonomous_functions[pth.default_island_name]) == 1
