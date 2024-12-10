
from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._030_data_portals.value_addresses import ValueAddr
from pythagoras._060_autonomous_functions import *

import pytest

@pytest.mark.parametrize("p",[0,0.5,1])
def test_load_save_error(tmpdir,p):
    with _PortalTester(
            AutonomousCodePortal
            , root_dict=tmpdir
            , default_island_name="test"
            , p_consistency_checks=p
            ) as t:
        assert len(t.portal.value_store) == 0
        def f(a, b):
            return a + b

        f_1 = AutonomousFn(f, island_name="123")
        f_1_address = ValueAddr(f_1)
        assert len(t.portal.value_store) == 1
        # assert f_1_address.get().island_name == "123"
        # f_1_address._invalidate_cache()
        # assert f_1_address.get().island_name == "123"
        f_1_address._invalidate_cache()

    with _PortalTester(
            AutonomousCodePortal
            , root_dict=tmpdir
            , default_island_name="test"
            , p_consistency_checks=p
            ) as t:

        def f(a, b):
            return a * b * 2

        f_2 = AutonomousFn(f, island_name="123")
        f_2_address = ValueAddr(f_2)
        assert len(t.portal.value_store) == 2
        f_2_address._invalidate_cache()
        assert f_2_address.get().island_name == "123"
        f_2_address._invalidate_cache()

    with _PortalTester(
            AutonomousCodePortal
            , root_dict=tmpdir
            , default_island_name="test"
            , p_consistency_checks=p
            ) as t:

        f_1_address._portal = t.portal
        f_2_address._portal = t.portal

        assert len(t.portal.value_store) == 2

        f_a = f_1_address.get()
        assert f_a(a=1, b=2) == 3

        with pytest.raises(Exception):
            f_b = f_2_address.get()