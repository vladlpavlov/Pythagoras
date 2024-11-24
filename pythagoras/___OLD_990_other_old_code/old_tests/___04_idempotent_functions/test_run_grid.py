from pythagoras.___04_idempotent_functions.idempotent_decorator import idempotent

from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)


def test_run_grid(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):

        @idempotent()
        def my_sum(x: float, y:float) -> float:
            return x + y

        grid = dict(
            x=[1, 2, 5]
            ,y=[10, 100, 1000])

        addrs = my_sum.run_grid(grid)
        results = [a.get() for a in addrs]
        assert sum(results) == 3354