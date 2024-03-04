import pytest

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth


def fibonacci(n: int) -> int:
    if n in [0, 1]:
        return n
    else:
        return fibonacci(n=n-1) + fibonacci(n=n-2)

def test_idp_fibonacci(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    global fibonacci
    fibonacci = idempotent()(fibonacci)

    assert fibonacci(n=50) == 12586269025