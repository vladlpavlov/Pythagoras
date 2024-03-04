from pythagoras._03_autonomous_functions import *
import pytest
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)
import pythagoras as pth



def test_2_didderent_functions_same_name(tmpdir):
    _clean_global_state()
    initialize(tmpdir)
    def f():
        return 1
    f_1 = autonomous(island_name="Moon")(f)
    f_2 = autonomous(island_name="Sun")(f)
    f_10 = strictly_autonomous()(f)

    assert f_1() == 1

    def f():
        return 2

    f_3 = autonomous(island_name="Earth")(f)
    with pytest.raises(Exception):
        f_4 = autonomous(island_name="Moon")(f)
    with pytest.raises(Exception):
        f_20 = strictly_autonomous()(f)

def test_2_similar_functions_same_name(tmpdir):
    _clean_global_state()
    initialize(tmpdir)
    def f():
        return 100
    f_1 = autonomous(island_name="Moon")(f)
    f_2 = autonomous(island_name="Sun")(f)
    f_10 = strictly_autonomous()(f)

    def f():
        """ This is a function """
        return 100 # This is a comment

    f_3 = autonomous(island_name="Earth")(f)
    f_4 = autonomous(island_name="Moon")(f)
    f_20 = strictly_autonomous()(f)

    assert f_1() == f_2() == f_3() == f_4() == f_10() == f_20() == 100