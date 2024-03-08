import pytest

from persidict import FileDirDict

from pythagoras._02_ordinary_functions.ordinary_decorator import ordinary
from pythagoras._03_autonomous_functions.autonomous_decorators import autonomous
from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._04_idempotent_functions.idempotent_func_and_address import (
    FunctionExecutionResultAddress)
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth

def test_list_execute(tmpdir):

    _clean_global_state()
    initialize(base_dir=tmpdir)

    @idempotent()
    def dbl(x: float) -> float:
        return x * 2

    input = []
    for i in range(4):
        input.append(dict(x=i))

    assert dbl.list_execute(input) == [0, 2, 4, 6]




