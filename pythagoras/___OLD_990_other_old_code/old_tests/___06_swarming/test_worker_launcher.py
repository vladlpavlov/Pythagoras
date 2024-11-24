from pythagoras.___06_swarming.background_workers import launch_background_worker
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)
import pythagoras as pth

def test_launch_background_worker(tmpdir):

    with _force_initialize(tmpdir, n_background_workers=0):
        p = launch_background_worker()

        @pth.idempotent()
        def f():
            return 5

        address = f.swarm()
        address._invalidate_cache()
        assert address.get() == 5