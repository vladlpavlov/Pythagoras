from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._020_logging_portals.logging_portals import (
    LoggingPortal, log_event)
import time

def test_event_logging_basic(tmpdir):
    with _PortalTester(LoggingPortal, tmpdir) as p:
        assert len(p.portal.event_log) == 0
        log_event("Hello, world!")
        assert len(p.portal.event_log) == 1

def test_exception_logging_basic(tmpdir):
    # tmpdir = 20*"Q"+str(int(time.time()))
    with _PortalTester(LoggingPortal, tmpdir) as p:
        assert len(p.portal.crash_history) == 0
        try:
            raise ValueError("This is a test exception.")
        except ValueError as e:
            LoggingPortal._exception_logger()
        assert len(p.portal.crash_history) == 1


def test_exception_logging_nested(tmpdir):
    # tmpdir = 20*"Q"+str(int(time.time()))
    # dir_2 = tmpdir+"D2"
    dir_2 = tmpdir.mkdir("D2")
    with _PortalTester(LoggingPortal, tmpdir) as p1:
        with LoggingPortal(dir_2) as portal_2:
            assert len(p1.portal.crash_history) == 0
            assert len(portal_2.crash_history) == 0
            try:
                raise ValueError("This is a test exception.")
            except ValueError as e:
                LoggingPortal._exception_logger()
            assert len(p1.portal.crash_history) == 1
            assert len(portal_2.crash_history) == 1
