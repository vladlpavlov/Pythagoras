import pytest
from pythagoras._03_autonomous_functions.autonomous_decorators import autonomous
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)


def isEven(n):
    if n == 0:
        return True
    else:
        return isOdd(n = n-1)


def isOdd(n):
    if n == 0:
        return False
    else:
        return isEven(n = n-1)


def test_no_decorators(tmpdir):
    with initialize(base_dir=tmpdir, n_background_workers=0):
        assert isOdd(n=4) == False
        assert isEven(n=4) == True


def test_one_decorator(tmpdir):
    with initialize(base_dir=tmpdir, n_background_workers=0):
        global isEven,  isOdd
        isEven = autonomous()(isEven)
        with pytest.raises(Exception):
            assert isOdd(n=4) == False
        with pytest.raises(Exception):
            assert isEven(n=4) == True

def test_two_decorators(tmpdir):
    with initialize(base_dir=tmpdir, n_background_workers=0):
        global isEven, isOdd
        isEven = autonomous()(isEven)
        isOdd = autonomous()(isOdd)
        assert isOdd(n=4) == False
        assert isEven(n=4) == True