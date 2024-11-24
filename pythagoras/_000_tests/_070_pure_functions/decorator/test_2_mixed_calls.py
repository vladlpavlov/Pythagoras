from pythagoras._060_autonomous_functions.autonomous_decorators import (
    autonomous)
from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
import pytest


def f_a():
    return 5

def f_i():
    return f_a()

def test_2_mixed_calls(tmpdir):
    global f_a, f_i
    with _PortalTester(PureCodePortal, tmpdir) as t:
        assert f_a() == 5
        assert f_i() == 5
        f_a = autonomous()(f_a)
        f_i = pure()(f_i)

        assert f_a() == 5
        assert f_i() == 5

