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

def test_chained_save_load(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        global f1, f2, f3, f4

        f1 = pure()(f1)
        f2 = pure()(f2)
        f3 = pure()(f3)

        assert f3() == 0
        assert f4() == 0

        address_3 = ValueAddr(f3)
        assert address_3.get()() == 0

    address_3._invalidate_cache()

    with _PortalTester(PureCodePortal, tmpdir) as t:
        del f1, f2, f3, f4

        address_3._portal = t.portal
        new_f3 = address_3.get()
        result = new_f3()
        assert result == 0
