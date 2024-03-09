from copy import deepcopy
from time import sleep
from pythagoras._06_swarming.background_worker import (
    launch_background_worker, process_random_execution_request)
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state)
import pythagoras as pth

def test_random_request_execution(tmpdir):
    _clean_global_state()
    pth.initialize(tmpdir, n_background_workers=0)

    @pth.idempotent()
    def f(n):
        return 5*n

    address = f.swarm(n=10)

    init_params = deepcopy(pth.initialization_parameters)

    _clean_global_state()

    process_random_execution_request(init_params)

    result = address.get()
    assert result == 50
    assert address.function(n=-1) == -5



