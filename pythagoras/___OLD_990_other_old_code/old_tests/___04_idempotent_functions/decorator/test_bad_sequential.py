import pytest
from pythagoras.___04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)


def test_bad_sequential(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):

        @idempotent()
        def my_function(x:int)->int:
            return x

        assert my_function(x=-2) == -2

        with pytest.raises(AssertionError):
            @idempotent()
            def my_function(x:int)->int:
                return x*1000