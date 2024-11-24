from pythagoras.___04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)


def f_before(**kwargs):
    return sum(kwargs.values())

def test_basics(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):

        f_after = idempotent()(f_before)

        args_dict = dict()
        for i in range(10):
            arg_name = f"arg_{i}"
            args_dict[arg_name] = i
            assert f_after(**args_dict) == f_before(**args_dict)
