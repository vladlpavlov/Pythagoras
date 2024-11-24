import pytest, time
import pythagoras as pth
from pythagoras import BasicPortal
from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal)
from pythagoras._070_pure_functions.pure_decorator import pure



def test_basic_addr(tmpdir):
    # tmpdir = 25*"Q" + str(int(time.time()))
    addr = None
    with _PortalTester(PureCodePortal, tmpdir):
        @pth.strictly_autonomous()
        def do_nothing():
            pass

        @pth.pure(guards = "do_nothing")
        def do_nothing_pure():
            return 10

        addr = do_nothing_pure.swarm()

    addr._invalidate_cache()

    with _PortalTester(PureCodePortal, tmpdir) as t:
        del do_nothing_pure
        del do_nothing
        addr._portal = t.portal
        result = addr.execute()
        assert result == 10


def test_changed_validators(tmpdir):
    # tmpdir = 25 * "Q" + str(int(time.time()))
    with _PortalTester(PureCodePortal, tmpdir):
        @pth.strictly_autonomous()
        def do_something_1():
            pass

        @pth.strictly_autonomous()
        def do_something_2():
            pass

        @pth.pure(guards = do_something_1)
        def do_something_pure():
            return 10

        @pth.pure(guards=do_something_1)
        def do_something_pure():
            return 10

        with pytest.raises(Exception):
            @pth.pure(guards=do_something_2)
            def do_something_pure():
                return 10