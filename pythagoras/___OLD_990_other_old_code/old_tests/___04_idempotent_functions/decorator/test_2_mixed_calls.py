from pythagoras.___03_OLD_autonomous_functions.autonomous_decorators import autonomous
from pythagoras.___04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)


def f_a():
    return 5

def f_i():
    return f_a()

def test_2_mixed_calls(tmpdir):
    global f_a, f_i
    with _force_initialize(tmpdir, n_background_workers=0):
        assert f_a() == 5
        assert f_i() == 5
        f_a = autonomous()(f_a)
        f_i = idempotent()(f_i)

        assert f_a() == 5
        assert f_i() == 5

