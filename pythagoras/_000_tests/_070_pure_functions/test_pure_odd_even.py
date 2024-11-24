import pytest
from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal, PureFn)
from pythagoras._070_pure_functions.pure_decorator import pure


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
    with _PortalTester(PureCodePortal, tmpdir) as t:
        assert isOdd(n=4) == False
        assert isEven(n=4) == True


def test_one_decorator_odd(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:
        global isEven,  isOdd
        old_isOdd = isOdd
        old_isEven = isEven

        isEven = pure()(isEven)
        with pytest.raises(Exception):
            assert isOdd(n=4) == False

        isEven = old_isEven
        isOdd = old_isOdd


def test_one_decorator_even(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:
        global isEven,  isOdd
        old_isOdd = isOdd
        old_isEven = isEven

        isEven = pure()(isEven)
        with pytest.raises(Exception):
            assert isEven(n=4) == True

        isEven = old_isEven
        isOdd = old_isOdd

@pytest.mark.parametrize("p",[0, 0.5, 1])
def test_two_decorators(tmpdir,p):
    # tmpdir = "YIYIYIYIYIYIYIYIYIYIYIYIYIYIYIY"
    with _PortalTester(PureCodePortal
            , tmpdir.mkdir("asd")
            , p_consistency_checks = p) as t:
        global isEven, isOdd
        old_isOdd = isOdd
        old_isEven = isEven

        isEven = pure()(isEven)
        isOdd = pure()(isOdd)
        for i in range(10):
            assert isOdd(n=24) == False
            assert isEven(n=24) == True

        isEven = old_isEven
        isOdd = old_isOdd

        value_store = t.portal.value_store
        assert value_store._total_checks_count == value_store._successful_checks_count
        if p > 0:
            assert value_store._total_checks_count > 0
        else:
            assert value_store._total_checks_count == 0

        execution_results = t.portal.execution_results
        assert execution_results._total_checks_count == execution_results._successful_checks_count
        if p > 0:
            assert execution_results._total_checks_count > 0
        else:
            assert execution_results._total_checks_count == 0