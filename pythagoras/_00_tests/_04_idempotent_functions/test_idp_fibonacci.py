
from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._07_mission_control.global_state_management import (
    _force_initialize)


def fibonacci(n: int) -> int:
    if n in [0, 1]:
        return n
    else:
        return fibonacci(n=n-1) + fibonacci(n=n-2)

def test_idp_fibonacci(tmpdir):
    # tmpdir = "YIYIYIYIYIYIYIYIYIYIYIYIYIYIYIYIY"
    with _force_initialize(tmpdir, n_background_workers=0):
        global fibonacci
        fibonacci = idempotent()(fibonacci)
        assert fibonacci(n=50) == 12586269025