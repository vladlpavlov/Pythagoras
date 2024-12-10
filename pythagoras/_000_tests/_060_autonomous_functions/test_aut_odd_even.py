import pytest

from pythagoras._010_basic_portals.portal_tester import _PortalTester

from pythagoras._060_autonomous_functions import *


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

    with _PortalTester(AutonomousCodePortal, root_dict=tmpdir):
        assert isOdd(n=4) == False
        assert isEven(n=4) == True


def test_one_decorator(tmpdir):
    with _PortalTester(AutonomousCodePortal, root_dict=tmpdir):
        global isEven,  isOdd
        oldIsEven = isEven
        oldIsOdd = isOdd
        isEven = autonomous()(isEven)
        with pytest.raises(Exception):
            assert isOdd(n=4) == False
        with pytest.raises(Exception):
            assert isEven(n=4) == True
        isEven = oldIsEven
        isOdd = oldIsOdd

def test_two_decorators(tmpdir):
    with _PortalTester(AutonomousCodePortal, root_dict=tmpdir):
        global isEven, isOdd
        oldIsEven = isEven
        oldIsOdd = isOdd
        isEven = autonomous()(isEven)
        isOdd = autonomous()(isOdd)
        assert isOdd(n=4) == False
        assert isEven(n=4) == True
        isEven = oldIsEven
        isOdd = oldIsOdd