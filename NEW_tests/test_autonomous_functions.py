import pytest

from pythagoras.NEW_autonomous_functions import autonomous, is_autonomous

@autonomous
def good_global_f():
    from math import sqrt
    return sqrt(4)


from math import sqrt
@autonomous
def bad_global_f1():
    return sqrt(4)

import sys

@autonomous
def bad_global_f2():
    return sys.version

def test_globals():
    """Test autonomous function wrapper with global objects."""

    assert good_global_f() == 2
    with pytest.raises(NameError):
        bad_global_f1()
    with pytest.raises(NameError):
        bad_global_f2()

    assert is_autonomous(good_global_f)
    assert not is_autonomous(bad_global_f1)
    assert not is_autonomous(bad_global_f2)


def test_locals():
    """Test autonomous function wrapper with local objects."""

    import random

    def bad_local_f3():
        x = 3
        return random.random()

    with pytest.raises(NameError):
        bad_local_f3 = autonomous(bad_local_f3)

    @autonomous
    def good_local_f2():
        import random
        x=3
        return random.random() + 1

    assert good_local_f2()

    assert is_autonomous(good_local_f2)
    assert not is_autonomous(bad_local_f3)