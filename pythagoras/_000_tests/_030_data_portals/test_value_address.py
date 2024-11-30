import time
from copy import copy
import pytest
from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._030_data_portals import *



values_to_test = [1, 10, 10.0, "ten", "10", 10j
    , True, None, [1,2,3],(1,2,3), {1,2,3}, {"zxcvbn":2, "qwerty":4, "b": "c"}]

@pytest.mark.parametrize("p",[1,0.5,0])
def test_value_address_basic(tmpdir,p):
    # tmpdir = 3*"VALUE_ADDRESS_BASIC_" + str(int(time.time())) + "_" + str(p)
    counter = 0

    with _PortalTester(DataPortal,tmpdir, p_consistency_checks=p) as t:
        portal = t.portal
        for v in values_to_test:
            assert len(portal.get_most_recently_entered_portal().value_store) == counter
            assert ValueAddr(v).get() == v
            assert ValueAddr(v).get() == v
            counter += 1
            assert len(portal.get_most_recently_entered_portal().value_store) == counter

    with _PortalTester(DataPortal,tmpdir, p_consistency_checks=p):
        assert len(portal.get_most_recently_entered_portal().value_store) == counter

@pytest.mark.parametrize("p",[0,0.5,1])
def test_nested_value_addrs(tmpdir,p):
    counter = 0

    with _PortalTester(DataPortal,tmpdir, p_consistency_checks=p):
        for v in values_to_test:
            assert len(DataPortal.get_most_recently_entered_portal().value_store) == counter
            assert ValueAddr([ValueAddr(v)]).get()[0].get() == v
            assert ValueAddr([ValueAddr(v)]).get()[0].get() == v
            counter += 2
            assert len(DataPortal.get_most_recently_entered_portal().value_store) == counter

    with _PortalTester(DataPortal,tmpdir, p_consistency_checks=p):
        assert len(DataPortal.get_most_recently_entered_portal().value_store) == counter


@pytest.mark.parametrize("p",[0,0.5,1])
def test_value_address_constructor_with_two_portals(tmpdir,p):

    with _PortalTester(DataPortal,tmpdir, p_consistency_checks=p):
        portal1 =DataPortal(tmpdir + "/t1", p_consistency_checks=p)
        portal2 =DataPortal(tmpdir + "/t2", p_consistency_checks=p)

        with portal1:
            addr1_10 = ValueAddr(10)
            with portal2:
                addr2_10 = ValueAddr(10)
                addr2_20 = ValueAddr(20)
                addr2_hihi = ValueAddr("hihi")

            assert len(portal1.value_store) == 1
            assert len(portal2.value_store) == 3

            addr1_10_new = ValueAddr(addr1_10)
            assert len(portal1.value_store) == 1
            assert len(portal2.value_store) == 3

            addr1_hihi = ValueAddr(addr2_hihi)
            assert len(portal1.value_store) == 2
            assert len(portal2.value_store) == 3


def test_value_address_ready_with_two_portals(tmpdir):

    with _PortalTester(DataPortal,tmpdir):
        portal1 =DataPortal(tmpdir + "/t1")
        portal2 =DataPortal(tmpdir + "/t2")

        with portal1:
            addr1_10 = ValueAddr(10)
            with portal2:
                addr2_10 = ValueAddr(10)
                addr2_20 = ValueAddr(20)
                addr2_hihi = ValueAddr("hihi")

            assert len(portal1.value_store) == 1
            assert len(portal2.value_store) == 3

            addr1_10_new = copy(addr1_10)
            assert len(portal1.value_store) == 1
            assert len(portal2.value_store) == 3

            addr1_hihi = copy(addr2_hihi)
            addr1_hihi._portal = portal1
            assert len(portal1.value_store) == 1
            assert len(portal2.value_store) == 3

            assert addr1_hihi.ready
            assert len(portal1.value_store) == 2
            assert len(portal2.value_store) == 3


def test_value_address_get_with_two_portals(tmpdir):

    with _PortalTester():
        portal1 =DataPortal(tmpdir + "/t1")
        portal2 =DataPortal(tmpdir + "/t2")

        with portal1:
            addr1_10 = ValueAddr(10)
            with portal2:
                addr2_10 = ValueAddr(10)
                addr2_20 = ValueAddr(20)
                addr2_hihi = ValueAddr("hihi")

            assert addr2_hihi.get() == "hihi"
            assert len(portal1.value_store) == 1
            assert len(portal2.value_store) == 3

            addr1_10_new = copy(addr1_10)
            assert len(portal1.value_store) == 1
            assert len(portal2.value_store) == 3

            addr1_hihi = copy(addr2_hihi)
            addr1_hihi._portal = portal1
            assert len(portal1.value_store) == 1
            assert len(portal2.value_store) == 3

            assert addr1_hihi.get() == "hihi"
            assert len(portal1.value_store) == 2
            assert len(portal2.value_store) == 3