import pytest


from pythagoras._03_autonomous_functions.autonomous_decorators import autonomous
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)


def fibonacci(n: int) -> int:
    if n in [0, 1]:
        return n
    else:
        return fibonacci(n=n-1) + fibonacci(n=n-2)

def test_aut_fibonacci(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir,n_background_workers=0)

    global fibonacci
    fibonacci = autonomous()(fibonacci)

    assert fibonacci(n=10) == 55