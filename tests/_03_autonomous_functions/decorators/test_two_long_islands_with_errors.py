from pythagoras._03_autonomous_functions import *
from pythagoras._05_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pytest


def f_1():
    return 0


def f_2():
    return f_1()*10


def f_3():
    return f_2()*10


def f_4():
    return f_3()*10


def f_5():
    return f_4()*10


def f_6():
    return f_5()*10


def test_two_chains_with_errors(tmpdir):
    _clean_global_state()
    initialize(tmpdir)
    global f_1, f_2, f_3, f_4, f_5, f_6

    f_1 = autonomous(island_name="Moon")(f_1)
    f_2 = autonomous(island_name="Moon")(f_2)
    f_3 = autonomous(island_name="Moon")(f_3)
    f_4 = autonomous(island_name="Sun")(f_4)
    f_5 = autonomous(island_name="Sun")(f_5)
    f_6 = autonomous(island_name="Sun")(f_6)


    assert f_1() == 0
    assert f_2() == 0
    assert f_3() == 0
    with pytest.raises(Exception):
        assert f_4() == 0
    with pytest.raises(Exception):
        assert f_5() == 0
    with pytest.raises(Exception):
        assert f_6() == 0