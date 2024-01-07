import pytest

from pythagoras.function_decorators.idempotent_decorator import idempotent
from pythagoras.function_decorators.idempotency_checks import is_idempotent
from pythagoras.misc_utils.global_state_management import (
    _clean_global_state, initialize)


def test_basics(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")
    def f_ab(a, b):
        return a + b

    result = f_ab(a=1,b=2)
    assert not is_idempotent(f_ab)
    f_1 = idempotent()(f_ab)
    #
    assert is_idempotent(f_1)
    assert f_1(a=1,b=2) == result

def test_init_checks(tmpdir):
    _clean_global_state()
    def f():
        pass

    with pytest.raises(AssertionError):
        idempotent()(f)

    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")

    idempotent()(f)