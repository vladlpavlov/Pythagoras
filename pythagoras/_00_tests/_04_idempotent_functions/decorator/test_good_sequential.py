import pytest

from pythagoras._01_foundational_objects.value_addresses import ValueAddress

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth




def test_good_sequential(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    @idempotent()
    def my_function(x:int)->int:
        return x*10

    assert my_function(x=1) == 10

    @idempotent()
    def my_function(x:int)->int: # comment
        """docstring"""
        return x*10

    assert my_function(x=2) == 20
