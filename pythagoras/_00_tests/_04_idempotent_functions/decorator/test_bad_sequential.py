import pytest
from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)


def test_bad_sequential(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    @idempotent()
    def my_function(x:int)->int:
        return x

    assert my_function(x=-2) == -2

    with pytest.raises(AssertionError):
        @idempotent()
        def my_function(x:int)->int:
            return x*1000