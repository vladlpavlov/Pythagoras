import pythagoras as pth

from pythagoras.___04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)


def test_print(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):

        @idempotent()
        def f(n:int):
            print(f"<{n}>")

        for i in range(1,4):
            f(n=i)
            f(n=i)
            assert (len(pth.default_portal.run_history.txt) == i)