import pytest

from persidict import FileDirDict

from pythagoras._02_ordinary_functions.ordinary_decorator import ordinary
from pythagoras._03_autonomous_functions.autonomous_decorators import autonomous
from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth


def factorial(n: int) -> int:
    if n in [0, 1]:
        return 1
    else:
        return n * factorial(n=n - 1)

def get_factorial_address(n:int, dir):
    with initialize(dir, n_background_workers=0):
        new_factorial = idempotent()(factorial)
        address = new_factorial.swarm(n=n)
        address._invalidate_cache()
        return address

def test_swarming_factorial(tmpdir):
    address = get_factorial_address(n=5, dir=tmpdir)
    with initialize(tmpdir, n_background_workers=2):
        print(f"{pth.runtime_id=}")
        assert address.get() == 120