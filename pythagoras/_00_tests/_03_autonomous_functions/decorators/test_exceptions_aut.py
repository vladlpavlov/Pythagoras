import pytest

from pythagoras._03_autonomous_functions import autonomous
from pythagoras._05_mission_control.global_state_management import (
    _clean_global_state, initialize)

import pythagoras as pth


def test_zero_div(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    @autonomous()
    def zero_div(x:float)->float:
        return x/0

    with pytest.raises(ZeroDivisionError):
        zero_div(x=2024)

    assert len(pth.crash_history) == 1
    for event_id  in list(pth.crash_history):
        assert "ZeroDivisionError" in event_id[1]
        assert "zero_div" in event_id[1]

def test_sqrt(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    @autonomous()
    def my_sqrt(x: float) -> float:
        from math import sqrt
        return sqrt(x)

    n = 5
    for i in range(n):
        if i <= 0:
            my_sqrt(x=-i)
            continue
        with pytest.raises(ValueError):
            my_sqrt(x=-i)

    assert len(pth.crash_history) == n - 1
    for event_id in list(pth.crash_history):
        assert "ValueError" in event_id[1]
        assert "my_sqrt" in event_id[1]
