from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
from pythagoras._030_data_portals.value_addresses import ValueAddr
import pytest

import pythagoras as pth


def f1():
    return 0

def f2():
    return f1()*2

def f3():
    return f2()*3

def f4():
    return f3()*4

def test_conflicted_chained_save_load(tmpdir):
    global f1, f2, f3, f4
    with _PortalTester(PureCodePortal, tmpdir) as t:
        f1 = pure()(f1)
        f2 = pure()(f2)
        f3 = pure()(f3)
        f4 = pure()(f4)

        assert f3() == 0
        assert f4() == 0

        address_2 = ValueAddr(f2)
        address_4 = ValueAddr(f4)

        assert address_2.get()() == 0
        assert address_4.get()() == 0

    address_2._invalidate_cache()
    address_4._invalidate_cache()

    with _PortalTester(PureCodePortal, tmpdir) as t:
        del f1, f2, f3, f4

        address_2._portal = t.portal
        address_4._portal = t.portal

        @pure()
        def f3():
            return 2024

        assert address_2.get()() == 0

        with pytest.raises(Exception):
            address_4.get()

