import pytest

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._05_mission_control.global_state_management import (
    _clean_global_state, initialize)


def test_init_checks(tmpdir):
    _clean_global_state()
    def f():
        pass

    with pytest.raises(AssertionError):
        idempotent()(f)

    _clean_global_state()
    initialize(base_dir=tmpdir)

    idempotent()(f)
