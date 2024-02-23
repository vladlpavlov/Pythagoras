import pytest

from pythagoras._03_autonomous_functions import *

import sys

def test_globals():
    """Test autonomous function wrapper with global objects."""
    @autonomous()
    def good_global_f():
        import math
        return math.sqrt(4)

    from math import sqrt

    def bad_global_f1():
        return sqrt(4)

    def bad_global_f2():
        return sys.version

    assert good_global_f() == 2

    with pytest.raises(Exception):
        bad_global_f1 = autonomous()(bad_global_f1)

    with pytest.raises(Exception):
        bad_global_f1 = autonomous()(bad_global_f1)

    assert is_autonomous(good_global_f)
    assert not is_autonomous(bad_global_f1)
    assert not is_autonomous(bad_global_f2)


def test_locals_2():
    """Test autonomous function wrapper with local objects."""

    import random

    def bad_local_f3():
        x = 3
        return random.random()

    with pytest.raises(Exception):
        bad_local_f3 = autonomous()(bad_local_f3)

    @autonomous()
    def good_local_f2():
        import random
        x=3
        return random.random() + 1

    assert good_local_f2()

    assert is_autonomous(good_local_f2)
    assert not is_autonomous(bad_local_f3)

def test_non_classic_callables():
    with pytest.raises(Exception):
        autonomous()(lambda x: x**2)

    class A:
        def __call__(self, x):
            return x**2

        def a_method(self,x):
            return x**2

        @classmethod
        def c_method(cls,x):
            return x**2

    a = A()

    with pytest.raises(Exception):
        autonomous()(A)

    with pytest.raises(Exception):
        autonomous()(a.a_method)

    with pytest.raises(Exception):
        autonomous()(A.c_method)


def test_yield():
    with pytest.raises(Exception):
        @autonomous()
        def f():
            yield 1

def test_nested_yield():
    @autonomous()
    def f():
        def g():
            yield 1
        return g()