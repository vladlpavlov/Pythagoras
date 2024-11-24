import time

import pytest
import pythagoras as pth
from pythagoras import BasicPortal
from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal)
from pythagoras._070_pure_functions.pure_decorator import pure

from pythagoras._050_safe_functions.package_manager import *


def test_real_package_installation_via_guard(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir):

        try:
            uninstall_package("nothing")
        except:
            pass


        with pytest.raises(ImportError):
            package = importlib.import_module("nothing")
            importlib.reload(package)


        @pth.strictly_autonomous()
        def check_nothing():
            try:
                import nothing
            except:
                pth.install_package("nothing")


        @pth.pure(guards = [check_nothing])
        def do_something():
            import nothing
            return 10

        assert do_something() == 10

        try:
            uninstall_package("nothing")
        except:
            pass

        with pytest.raises(ImportError):
            package = importlib.import_module("nothing")
            importlib.reload(package)



def test_fake_package_installation_via_guard(tmpdir):
    # tmpdir = "FAKE_PACKAGE_INSTALLATION_VIA_GUARD_"+str(int(time.time()))
    with _PortalTester(PureCodePortal, tmpdir):

        try:
            uninstall_package("p1q9m2x8d3h8r56")
        except:
            pass

        with pytest.raises(BaseException):
            import p1q9m2x8d3h8r56


        @pth.strictly_autonomous()
        def check_nonexisting():
            try:
                import p1q9m2x8d3h8r56
            except:
                pth.install_package("p1q9m2x8d3h8r56")


        @pth.pure(guards = check_nonexisting)
        def do_weird_thing():
            import p1q9m2x8d3h8r56
            return 10


        with pytest.raises(Exception):
            do_weird_thing()

        try:
            uninstall_package("p1q9m2x8d3h8r56")
        except:
            pass
