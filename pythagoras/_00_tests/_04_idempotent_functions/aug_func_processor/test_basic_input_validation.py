import pytest
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)
from pythagoras._04_idempotent_functions.process_augmented_func_src import (
    process_augmented_func_src)

src_1_good ="""
@pth.autonomous(island_name='DEMO')
def f_1_1():
    pass
    
@pth.autonomous()
def f_1_2():
    pass
"""

src_2_bad_random = """
Some random string
"""

src_3_bad_no_decorators = """
def f_3():
    pass
"""

src_4_bad_wrong_decorator = """
@pth.non_existent_decorator()
def f_3():
    pass
"""

src_5_good_many_functions = """
@pth.autonomous()
def f_5_1():
    pass

@pth.autonomous(island_name='DEMO')
def f_5_2():
    pass
    
@pth.strictly_autonomous()
def f_5_3():
    pass

# @pth.idempotent()
# def f_5_4():
#     pass
"""


def test_basic_input_validation(tmpdir):
    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)
    process_augmented_func_src(src_1_good)

    with pytest.raises(Exception):
        process_augmented_func_src(src_2_bad_random)

    with pytest.raises(Exception):
        process_augmented_func_src(src_3_bad_no_decorators)

    with pytest.raises(Exception):
        process_augmented_func_src(src_4_bad_wrong_decorator)

    process_augmented_func_src(src_5_good_many_functions)