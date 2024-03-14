import pytest
import pythagoras as pth
from pythagoras._07_mission_control.global_state_management import (
    _force_initialize)


def test_basic_execution(tmpdir):
    with _force_initialize(tmpdir, n_background_workers = 0):
        @pth.strictly_autonomous()
        def do_nothing():
            pass

        @pth.idempotent(validators = do_nothing)
        def do_nothing_idempotent():
            return 10


        assert do_nothing_idempotent() == 10


def test_basic_exception(tmpdir):
    with _force_initialize(tmpdir, n_background_workers = 0):
        @pth.strictly_autonomous()
        def no_go():
            assert False, "This validator will always fail."

        @pth.idempotent(validators = no_go)
        def do_nothing_idempotent():
            return 10

        with pytest.raises(Exception):
            do_nothing_idempotent()


def test_basic_addr(tmpdir):
    # tmpdir = "JJUJUJUJUJUJUJUJUJUJUJUJU"
    addr = None
    with _force_initialize(tmpdir, n_background_workers = 0):
        @pth.strictly_autonomous()
        def do_nothing():
            pass

        @pth.idempotent(validators = do_nothing)
        def do_nothing_idempotent():
            return 10


        addr = do_nothing_idempotent.swarm()

    with _force_initialize(tmpdir, n_background_workers=0):
        assert addr.execute() == 10


def test_changed_validators(tmpdir):
    with _force_initialize(tmpdir, n_background_workers = 0):
        @pth.strictly_autonomous()
        def do_nothing_1():
            pass

        @pth.strictly_autonomous()
        def do_nothing_2():
            pass

        @pth.idempotent(validators = do_nothing_1)
        def do_nothing_idempotent():
            return 10

        @pth.idempotent(validators=do_nothing_1)
        def do_nothing_idempotent():
            return 10

        with pytest.raises(Exception):
            @pth.idempotent(validators=do_nothing_2)
            def do_nothing_idempotent():
                return 10