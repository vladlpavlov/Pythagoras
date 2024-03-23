from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent

from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, _force_initialize)


def test_list_execute(tmpdir):

    with (_force_initialize(tmpdir, n_background_workers=0)):

        @idempotent()
        def dbl(x: float) -> float:
            return x * 2

        input = []
        for i in range(4):
            input.append(dict(x=i))

        addrs = dbl.run_list(input)
        results = [a.get() for a in addrs]
        assert results == [0, 2, 4, 6]