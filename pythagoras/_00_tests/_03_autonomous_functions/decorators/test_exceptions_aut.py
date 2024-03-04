import pytest

from pythagoras._03_autonomous_functions import autonomous
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)
from pythagoras._05_events_and_exceptions.current_date_gmt_str import (
    current_date_gmt_string)

import pythagoras as pth


def test_zero_div(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    date_str_1 = current_date_gmt_string()

    @autonomous()
    def zero_div(x:float)->float:
        return x/0

    with pytest.raises(ZeroDivisionError):
        zero_div(x=2024)

    date_str_2 = current_date_gmt_string()

    assert len(pth.global_crash_history) == 1
    for event_id  in list(pth.global_crash_history):
        assert "ZeroDivisionError" in event_id[1]
        assert "zero_div" in event_id[1]
        assert event_id[0] in [date_str_1, date_str_2]

def test_sqrt(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    @autonomous()
    def my_sqrt(x: float) -> float:
        from math import sqrt
        return sqrt(x)

    date_str_1 = current_date_gmt_string()

    n = 5
    for i in range(n):
        if i <= 0:
            my_sqrt(x=-i)
            continue
        with pytest.raises(ValueError):
            my_sqrt(x=-i)

    date_str_2 = current_date_gmt_string()

    assert len(pth.global_crash_history) == n - 1
    for event_id in list(pth.global_crash_history):
        assert "ValueError" in event_id[1]
        assert "my_sqrt" in event_id[1]
        assert event_id[0] in [date_str_1, date_str_2]
