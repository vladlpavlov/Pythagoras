import pytest

from persidict import FileDirDict

from pythagoras._02_ordinary_functions.ordinary_decorator import ordinary
from pythagoras._03_autonomous_functions.autonomous_decorators import autonomous
from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, _force_initialize)

import pythagoras as pth



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