import pytest

from persidict import FileDirDict

from pythagoras._02_ordinary_functions.ordinary_decorator import ordinary
from pythagoras._03_autonomous_functions.autonomous_decorators import autonomous
from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._04_idempotent_functions.idempotent_func_and_address import (
    FuncOutputAddress)
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth


def factorial(n:int) -> int:
    if n in [0, 1]:
        return 1
    else:
        return n * factorial(n=n-1)

def test_idp_factorial(tmpdir):

    _clean_global_state()
    initialize(base_dir=tmpdir)

    global factorial
    factorial = idempotent()(factorial)

    addr_5 = FuncOutputAddress(f=factorial, arguments=dict(n=5))

    with pytest.raises(TimeoutError):
        addr_5.get(timeout=2)

    function = addr_5.function
    arguments = addr_5.arguments
    name = addr_5.f_name
    assert name == "factorial"
    assert function(**arguments) == 120



