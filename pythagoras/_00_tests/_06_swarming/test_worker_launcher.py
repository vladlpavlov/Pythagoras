from time import sleep
from pythagoras._06_swarming.background_worker import (
    launch_background_worker)
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state)
import pythagoras as pth

def test_launch_background_worker(tmpdir):
    _clean_global_state()

    pth.initialize(tmpdir, n_background_workers=0)
    p = launch_background_worker()

    @pth.idempotent()
    def f():
        return 5

    address = f.swarm()
    assert address.get() == 5

