
from pythagoras._03_autonomous_functions import *
import pythagoras as pth
from pythagoras._03_autonomous_functions.default_island_singleton import DefaultIsland

from persidict import FileDirDict

pth.function_source_repository = FileDirDict("___FileDirDict___")

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

@autonomous(island_name="DEMO")
def zyx(a:int):
    b=10
    return a+b

def test_autonomous():
    assert not is_strictly_autonomous(zyx)
    assert  is_loosely_autonomous(zyx)
    assert is_autonomous(zyx)
    assert zyx(a=10) == 20

@autonomous(island_name=DefaultIsland)
def f_1():
    return 1000

@autonomous(island_name=DefaultIsland)
def f_2():
    return f_1() + 10

def test_default_island_chained():
    assert f_1() == 1000
    assert f_2() == 1010



@autonomous(island_name="Moon")
def g_2():
    return g_1() + 10

@autonomous(island_name="Moon")
def g_1():
    return 1000

def test_chained_reversed_order():
    assert g_1() == 1000
    assert g_2() == 1010


