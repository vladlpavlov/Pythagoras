import pythagoras as pth
from pythagoras._07_mission_control.global_state_management import (
    _force_initialize)

def test_launch_background_worker_from_init(tmpdir):

    with _force_initialize(tmpdir, n_background_workers=1):

        @pth.idempotent()
        def sample_f(s:str) -> str:
            return 2*s

        address = sample_f.swarm(s="hello")
        address._invalidate_cache()
        assert address.get() == "hellohello"

