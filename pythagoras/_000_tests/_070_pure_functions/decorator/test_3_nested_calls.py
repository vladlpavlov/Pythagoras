from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
from pythagoras._070_pure_functions.purity_checks import is_pure


def a():
    return 2

def b():
    return a()*2

def c():
    return b()*2

def test_2_nested_calls(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        global a, b, c

        assert not is_pure(a)
        assert not is_pure(b)
        assert not is_pure(c)

        assert a() == 2
        assert b() == 4
        assert c() == 8


        c = pure()(c)
        a = pure()(a)
        b = pure()(b)

        assert is_pure(a)
        assert is_pure(b)
        assert is_pure(c)

        assert c() == 8