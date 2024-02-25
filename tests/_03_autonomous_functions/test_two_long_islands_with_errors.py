from pythagoras._03_autonomous_functions import *
import pytest

@autonomous(island_name="Moon")
def f_1():
    return 0

@autonomous(island_name="Moon")
def f_2():
    return f_1()*10

@autonomous(island_name="Moon")
def f_3():
    return f_2()*10

@autonomous(island_name="Sun")
def f_4():
    return f_3()*10

@autonomous(island_name="Sun")
def f_5():
    return f_4()*10

@autonomous(island_name="Sun")
def f_6():
    return f_5()*10


def test_two_chains_with_errors():
    assert f_1() == 0
    assert f_2() == 0
    assert f_3() == 0
    with pytest.raises(Exception):
        assert f_4() == 0
    with pytest.raises(Exception):
        assert f_5() == 0
    with pytest.raises(Exception):
        assert f_6() == 0