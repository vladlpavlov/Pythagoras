from pythagoras._030_data_portals.value_addresses import ValueAddr
from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
import pytest


def my_function():
    return 2024

def test_basic_save_load(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        global my_function

        my_function = pure()(my_function)

        assert my_function() == 2024

        address = None
        # assert len(pth.value_store) == 0
        for i in range(3): address = ValueAddr(my_function)
        for i in range(3): assert address.get()() == 2024
        # assert len(pth.value_store) == 1