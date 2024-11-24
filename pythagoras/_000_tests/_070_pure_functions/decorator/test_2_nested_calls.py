from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal)
from pythagoras._070_pure_functions.purity_checks import is_pure
from pythagoras._070_pure_functions.pure_decorator import pure
import pytest



def f_nstd():
    return 5

def g_nstd():
    return f_nstd()

def test_2_nested_calls(tmpdir):
    global f_nstd, g_nstd
    with _PortalTester(PureCodePortal, tmpdir) as t:
        assert not is_pure(f_nstd)
        assert not is_pure(g_nstd)
        assert g_nstd() == 5
        g_nstd = pure()(g_nstd)
        f_nstd = pure()(f_nstd)
        assert is_pure(f_nstd)
        assert is_pure(g_nstd)
        assert g_nstd() == 5