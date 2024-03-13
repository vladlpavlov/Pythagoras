import pytest

from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)


# def test_init_checks(tmpdir):
#     _clean_global_state()
#     def f_1():
#         pass
#
#     def f_2():
#         pass
#
#     with pytest.raises(AssertionError):
#         idempotent()(f_1)
#
#     idempotent()(f_2)
#
#     _clean_global_state()
#     initialize(tmpdir, n_background_workers=0)
#
#     idempotent()(f_1)
#     idempotent()(f_2)

