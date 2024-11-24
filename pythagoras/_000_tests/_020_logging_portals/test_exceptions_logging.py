import os

from pythagoras import _PortalTester
from pythagoras import LoggingPortal



def test_exception_inside_with(tmpdir):
    with _PortalTester(LoggingPortal, tmpdir+"__12345") as p:
        assert len(p.portal.crash_history) == 0
        try:
            with p.portal:
                x = 1/0
        except:
            pass
        assert len(p.portal.crash_history) == 1


def test_sequential_exceptions_inside_with(tmpdir):
    with _PortalTester(LoggingPortal, tmpdir+"__QETUO") as p:
        assert len(p.portal.crash_history) == 0

        try:
            with p.portal:
                x = 1/0
        except:
            pass

        try:
            with p.portal:
                x = 1 / 0
        except:
            pass

        assert len(p.portal.crash_history) == 2

def test_exceptions_2_exceptions(tmpdir):
    with _PortalTester(LoggingPortal, tmpdir) as p:
        assert len(p.portal.crash_history) == 0
        try:
            with p.portal:
                x = 1/0
        except:
            pass

    with _PortalTester(LoggingPortal, tmpdir) as p:
        assert len(p.portal.crash_history) == 1

        try:
            with p.portal:
                x = 2/0
        except:
            pass

        assert len(p.portal.crash_history) == 2

def test_exception_inside_nested_with_same_portal(tmpdir):
    with _PortalTester(LoggingPortal, tmpdir+"__12Q3Q45") as p:
        assert len(p.portal.crash_history) == 0
        try:
            with p.portal:
                with p.portal:
                    x = 1/0
        except:
            pass
        assert len(p.portal.crash_history) == 1


def test_exception_inside_nested_with(tmpdir):
    with _PortalTester(LoggingPortal, tmpdir) as p:
        portal2=LoggingPortal(tmpdir+"_22")
        portal3=LoggingPortal(tmpdir+"_333")
        assert len(p.portal.crash_history) == 0
        assert len(portal2.crash_history) == 0
        assert len(portal3.crash_history) == 0
        with portal2:
            try:
                with p.portal:
                    raise Exception("This is a test exception")
            except:
                pass
            assert len(p.portal.crash_history) == 1
            assert len(portal2.crash_history) == 1
            assert len(portal3.crash_history) == 0
        assert len(p.portal.crash_history) == 1
        assert len(portal2.crash_history) == 1
        assert len(portal3.crash_history) == 0