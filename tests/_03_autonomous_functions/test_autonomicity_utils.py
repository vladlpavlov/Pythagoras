
from pythagoras._03_autonomous_functions import *

@strictly_autonomous()
def f(a:int):
    b=24
    return a+b

def test_strictly_autonomous():
    assert is_strictly_autonomous(f)
    assert not is_loosely_autonomous(f)
    assert is_autonomous(f)
    assert f(a=10) == 34


def h(a:int):
    b=100
    return a+b

def test_not_autonomous():
    assert not is_autonomous(h)
    assert not is_loosely_autonomous(h)
    assert not is_strictly_autonomous(h)
    assert h(a=10) == 110