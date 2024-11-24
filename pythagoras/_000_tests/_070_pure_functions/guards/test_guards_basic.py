import pytest, time
import pythagoras as pth
from pythagoras import BasicPortal
from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal)
from pythagoras._070_pure_functions.pure_decorator import pure


def test_basic_execution(tmpdir):
    # tmpdir = 25 * "Q" + str(int(time.time()))
    with _PortalTester(PureCodePortal, tmpdir):
        @pth.strictly_autonomous()
        def do_nothing():
            pass

        @pth.pure(guards = do_nothing)
        def do_nothing_pure():
            return 10


        assert do_nothing_pure() == 10


def test_basic_exception(tmpdir):
    # tmpdir = 25 * "Q" + str(int(time.time()))
    with _PortalTester(PureCodePortal, tmpdir):
        @pth.strictly_autonomous()
        def no_go():
            assert False, "This validator will always fail."

        @pth.pure(guards = no_go)
        def do_nothing_pure():
            return 10

        with pytest.raises(Exception):
            do_nothing_pure()


