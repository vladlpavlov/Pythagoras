from pythagoras.function_decorators.autonomous_decorators import *
from pythagoras.function_decorators.autonomicity_checks import *

@strictly_autonomous()
def f(a:int):
    b=24
    return a+b

def test_strictly_autonomous():
    assert is_strictly_autonomous(f)
    assert not is_loosely_autonomous(f)
    assert is_autonomous(f)
    assert f(10) == 34

# @loosely_autonomous()
# def g(a:int):
#     b=100
#     return a+b
#
# def test_loosely_autonomous():
#     assert is_loosely_autonomous(g)
#     assert not is_strictly_autonomous(g)
#     assert is_autonomous(g)
#     assert g(10) == 110

def h(a:int):
    b=100
    return a+b

def test_not_autonomous():
    assert not is_loosely_autonomous(h)
    assert not is_strictly_autonomous(h)
    assert not is_autonomous(h)
    assert h(10) == 110