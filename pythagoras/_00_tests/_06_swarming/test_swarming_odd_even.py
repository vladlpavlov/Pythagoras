import pytest
from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize, _force_initialize)


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
    with _force_initialize(tmpdir, n_background_workers=0):
        assert isOdd(n=400) == False
        assert isEven(n=400) == True


# def test_one_decorator_odd(tmpdir):
#     global isEven, isOdd
#     address = None
#     with initialize(tmpdir, n_background_workers=0):
#         isEven = idempotent()(isEven)
#         with pytest.raises(Exception):
#             address = isOdd.swarm(n=400)
#
#
# def test_one_decorator_even(tmpdir):
#     global isEven, isOdd
#     address = None
#     with initialize(tmpdir, n_background_workers=0):
#         isEven = idempotent()(isEven)
#         with pytest.raises(Exception):
#             address = isEven.swarm(n=400)


def test_two_decorators(tmpdir):
    global isEven, isOdd
    addr = None
    with _force_initialize(tmpdir, n_background_workers=0):
        isEven = idempotent()(isEven)
        isOdd = idempotent()(isOdd)
        addr = isEven.swarm(n=40)

    with _force_initialize(tmpdir, n_background_workers=5):
        addr._invalidate_cache()
        assert addr.get() == True
