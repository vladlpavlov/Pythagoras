from pythagoras.___04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras.___04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)


def test_basics(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):
        def f_ab(a, b):
            return a + b

        result = f_ab(a=1,b=2)
        assert not is_idempotent(f_ab)
        f_1 = idempotent()(f_ab)
        #
        assert is_idempotent(f_1)
        for i in range(3):
            assert f_1(a=1,b=2) == result