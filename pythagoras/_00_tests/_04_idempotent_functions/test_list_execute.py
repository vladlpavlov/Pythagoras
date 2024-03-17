from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent

from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)


def test_list_execute(tmpdir):

    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)

    @idempotent()
    def dbl(x: float) -> float:
        return x * 2

    input = []
    for i in range(4):
        input.append(dict(x=i))

    assert dbl.execute_list(input) == [0, 2, 4, 6]




