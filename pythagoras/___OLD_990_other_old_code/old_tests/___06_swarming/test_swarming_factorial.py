from pythagoras.___04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)

import pythagoras as pth


def factorial(n: int) -> int:
    if n in [0, 1]:
        return 1
    else:
        return n * factorial(n=n - 1)

def get_factorial_address(n:int, dir):
    with _force_initialize(dir, n_background_workers=0):
        new_factorial = idempotent()(factorial)
        address = new_factorial.swarm(n=n)
        address._invalidate_cache()
        return address

def test_swarming_factorial(tmpdir):
    address = get_factorial_address(n=5, dir=tmpdir)
    with _force_initialize(tmpdir, n_background_workers=2):
        address._portal = pth.default_portal
        assert address.get() == 120
