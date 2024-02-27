import pytest

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._05_mission_control.global_state_management import (
    _clean_global_state, initialize)


def f_before(**kwargs):
    return sum(kwargs.values())

def test_basics(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    f_after = idempotent()(f_before)

    args_dict = dict()
    for i in range(10):
        arg_name = f"arg_{i}"
        args_dict[arg_name] = i
        assert f_after(**args_dict) == f_before(**args_dict)
