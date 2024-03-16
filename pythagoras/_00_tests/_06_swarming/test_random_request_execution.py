from copy import deepcopy
from pythagoras._06_swarming.background_workers import (
    process_random_execution_request)
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state)
import pythagoras as pth

def test_random_request_execution(tmpdir):

    with pth.initialize(tmpdir, n_background_workers=0):

        @pth.idempotent()
        def f(n):
            return 5*n

        address = f.swarm(n=10)

        init_params = deepcopy(pth.initialization_parameters)
        init_params["runtime_id"] = None

    process_random_execution_request(init_params)

    address._invalidate_cache()
    result = address.get()
    assert result == 50
    assert address.function(n=-1) == -5
    _clean_global_state()





