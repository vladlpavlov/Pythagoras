
from pythagoras._030_data_portals.value_addresses import ValueAddr
from pythagoras._030_data_portals.data_portals import DataPortal

from pythagoras._010_basic_portals.portal_tester import _PortalTester


def test_value_address_basic(tmpdir):
    with _PortalTester():
        tmpdir1 = tmpdir + "/test_value_address_basic"
        tmpdir2 = tmpdir + "/hihi"

        portal1 = DataPortal(tmpdir1)
        portal2 = DataPortal(tmpdir2)

        with portal1:
            addr = ValueAddr(10)
            with portal2:
                addr = ValueAddr(10)
                addr = ValueAddr(10)
                addr = ValueAddr(12)

        assert len(portal1.value_store) == 1
        assert len(portal2.value_store) == 2


def test_nested_portals_whitebox(tmpdir):
    with _PortalTester():
        tmpdir1 = tmpdir + "/t1"
        tmpdir2 = tmpdir + "/t2"
        tmpdir3 = tmpdir + "/t3"

        assert len(DataPortal.all_portals) == 0
        portal1 = DataPortal(tmpdir1)
        assert len(DataPortal.all_portals) == 1
        portal2 = DataPortal(tmpdir2)
        assert len(DataPortal.all_portals) == 2
        portal3 = DataPortal(tmpdir3)
        assert len(DataPortal.all_portals) == 3

        with portal1:
            assert len(DataPortal.all_portals) == 3
            assert len(DataPortal.entered_portals_stack) == 1
            assert sum(DataPortal.entered_portals_counters_stack) == 1
            with portal2:
                assert len(DataPortal.all_portals) == 3
                assert len(DataPortal.entered_portals_stack) == 2
                assert sum(DataPortal.entered_portals_counters_stack) == 2
                with portal3:
                    assert len(DataPortal.all_portals) == 3
                    assert len(DataPortal.entered_portals_stack) == 3
                    assert sum(DataPortal.entered_portals_counters_stack) == 3

        with portal1:
            assert len(DataPortal.entered_portals_stack) == 1
            assert sum(DataPortal.entered_portals_counters_stack) == 1
            with portal2:
                assert len(DataPortal.entered_portals_stack) == 2
                assert sum(DataPortal.entered_portals_counters_stack) == 2
                with portal2:
                    assert len(DataPortal.entered_portals_stack) == 2
                    assert sum(DataPortal.entered_portals_counters_stack) == 3
                    with portal3:
                        assert len(DataPortal.entered_portals_stack) == 3
                        assert sum(DataPortal.entered_portals_counters_stack) == 4
                        with portal1:
                            assert len(DataPortal.entered_portals_stack) == 4
                assert len(DataPortal.entered_portals_stack) == 2
                assert sum(DataPortal.entered_portals_counters_stack) == 2
            assert len(DataPortal.entered_portals_stack) == 1
            assert sum(DataPortal.entered_portals_counters_stack) == 1


def test_get_portal_basic(tmpdir):
    with _PortalTester():
        tmpdir1 = tmpdir + "/t1"
        tmpdir2 = tmpdir + "/t2"
        tmpdir3 = tmpdir + "/t3"

        portal1 = DataPortal(tmpdir1)
        portal2 = DataPortal(tmpdir2)
        portal3 = DataPortal(tmpdir3)

        with portal1:
            assert portal1 == DataPortal.get_best_portal_to_use()
            with portal2:
                assert portal2 == DataPortal.get_best_portal_to_use()
                with portal3:
                    assert portal3 == DataPortal.get_best_portal_to_use()

        with portal1:
            assert portal1 == DataPortal.get_best_portal_to_use()
            with portal2:
                assert portal2 == DataPortal.get_best_portal_to_use()
                with portal2:
                    assert portal2 == DataPortal.get_best_portal_to_use()
                    with portal3:
                        assert portal3 == DataPortal.get_best_portal_to_use()
                        with portal1:
                            assert portal1 == DataPortal.get_best_portal_to_use()
                assert portal2 == DataPortal.get_best_portal_to_use()
            assert portal1 == DataPortal.get_best_portal_to_use()