import pytest
import pythagoras as pth
from pythagoras._07_mission_control.global_state_management import (
    _force_initialize)


def test_real_package_installation(tmpdir):
    with _force_initialize(tmpdir, n_background_workers = 0):

        try:
            pth.uninstall_package("nothing")
        except:
            pass

        with pytest.raises(ImportError):
            import nothing


        @pth.strictly_autonomous()
        def check_nothing():
            import nothing

        @pth.strictly_autonomous()
        def install_nothing():
            pth.install_package("nothing")


        @pth.idempotent(validators = check_nothing, correctors = install_nothing)
        def do_something():
            import nothing
            return 10

        assert do_something() == 10
        pth.uninstall_package("nothing")


def test_fake_package_installation(tmpdir):
    with _force_initialize(tmpdir, n_background_workers = 0):

        try:
            pth.uninstall_package("p1q9m2x8d3h8r6")
        except:
            pass

        with pytest.raises(ImportError):
            import p1q9m2x8d3h8r6


        @pth.strictly_autonomous()
        def check_nothing():
            import p1q9m2x8d3h8r6

        @pth.strictly_autonomous()
        def install_nothing():
            pth.install_package("p1q9m2x8d3h8r6")


        @pth.idempotent(validators = check_nothing, correctors = install_nothing)
        def do_something():
            import p1q9m2x8d3h8r6
            return 10


        with pytest.raises(Exception):
            do_something()
