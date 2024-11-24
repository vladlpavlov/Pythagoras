from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
from pythagoras._070_pure_functions.purity_checks import is_pure


def test_nested_from_import(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        @pure()
        def f(x:float)->float:
            from math import sqrt
            return sqrt(x)

        assert f(x=4) == 2


def test_nested_import_as(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        @pure()
        def f(x:float)->float:
            import math as mm
            return mm.sin(x)

        assert f(x=0) == 0

def test_nested_from_import_as(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        @pure()
        def f(x:float)->float:
            from math import log as l
            return l(x)

        assert f(x=1) == 0