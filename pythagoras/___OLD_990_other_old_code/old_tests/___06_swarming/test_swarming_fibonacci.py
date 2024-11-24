from pythagoras.___04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)

import pythagoras as pth

def fibonacci(n: int) -> int:
    if n in [0, 1]:
        return n
    else:
        return fibonacci(n=n-1) + fibonacci(n=n-2)

def test_swarming_fibonacci(tmpdir):
    global fibonacci
    address = None
    with _force_initialize(tmpdir, n_background_workers=0):
        fibonacci = idempotent()(fibonacci)
        address = fibonacci.swarm(n=50)

    with _force_initialize(tmpdir, n_background_workers=10):
        address._invalidate_cache()
        assert address.get() == 12586269025