from pythagoras.___04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)


def factorial(n:int) -> int:
    if n in [0, 1]:
        return 1
    else:
        return n * factorial(n=n-1)

def test_idp_factorial(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):
        global factorial
        factorial = idempotent()(factorial)
        assert factorial(n=5) == 120
        assert factorial(n=5) == 120