from pythagoras import BasicPortal
from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal)
from pythagoras._070_pure_functions.pure_decorator import pure



def simple_func(n: int) -> int:
    return 10 * n


def complex_func(n: int) -> int:
    return simple_func(n=n)

def test_addrr_execute(tmpdir):
    # tmpdir = "TTTTTTTTTTTTTTTTTTTTT"

    with _PortalTester(PureCodePortal, tmpdir):
        global simple_func, complex_func
        simple_func = pure()(simple_func)
        complex_func = pure()(complex_func)
        addr_10 = complex_func.get_address(n=0)


    with _PortalTester(PureCodePortal, tmpdir) as t:
        addr_10._invalidate_cache()
        addr_10._portal = t.portal
        assert addr_10.execute() == 0
        assert addr_10.function(n=1) == 10

