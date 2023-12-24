import pytest

from pythagoras.NEW_autonomous_functions import autonomous

@autonomous
def good_f():
    from math import sqrt
    return sqrt(4)


from math import sqrt
@autonomous
def bad_f1():
    return sqrt(4)

import sys

@autonomous
def bad_f2():
    return sys.version

def test_wrapper():
    """Test autonomous function wrapper."""

    assert good_f() == 2
    with pytest.raises(NameError):
        bad_f1()
    with pytest.raises(NameError):
        bad_f2()

    import random

    with pytest.raises(NameError):
        @autonomous
        def bad_f3():
            x=3
            return random.random()


