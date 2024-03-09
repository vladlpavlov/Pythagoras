from pythagoras._03_autonomous_functions import *
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)


def f_1():
    return 0

def f_2():
    return f_1()*10

def f_3():
    return f_2()*10

def f_4():
    return 10

def f_5():
    return f_4()*10

def f_6():
    return f_5()*10

def f_7():
    return f_3()*10

def test_two_chains_no_errors(tmpdir):
    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)

    global f_1, f_2, f_3, f_4, f_5, f_6, f_7

    f_1 = autonomous(island_name="QWERTY")(f_1)
    f_2 = autonomous(island_name="QWERTY")(f_2)
    f_3 = autonomous(island_name="QWERTY")(f_3)
    f_4 = autonomous(island_name="QWERTY")(f_4)
    f_5 = autonomous(island_name="QWERTY")(f_5)
    f_6 = autonomous(island_name="QWERTY")(f_6)
    f_7 = autonomous(island_name="QWERTY")(f_7)

    assert f_1() == 0
    assert len(f_1.dependencies) == 1
    assert f_2() == 0
    assert len(f_2.dependencies) == 2
    assert f_3() == 0
    assert len(f_3.dependencies) == 3
    assert f_4() == 10
    assert len(f_4.dependencies) == 1
    assert f_5() == 100
    assert len(f_5.dependencies) == 2
    assert f_6() == 1000
    assert len(f_6.dependencies) == 3
    assert f_7() == 0
    assert len(f_7.dependencies) == 4