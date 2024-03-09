import pytest

from pythagoras._04_idempotent_functions import idempotent
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize)
from pythagoras._05_events_and_exceptions.current_date_gmt_str import (
    current_date_gmt_string)

import pythagoras as pth


def test_zero_div(tmpdir):
    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)
    # initialize(base_dir="EEEEEEEEEEEEEEEEEEEE")

    date_str_1 = current_date_gmt_string()

    @idempotent()
    def zero_div(x:float)->float:
        return x/0

    with pytest.raises(ZeroDivisionError):
        zero_div(x=2024)

    date_str_2 = current_date_gmt_string()

    assert len(pth.crash_history) == 1
    for event_id  in list(pth.crash_history):
        assert "ZeroDivisionError" in event_id[1]
        assert "zero_div" in event_id[1]
        assert event_id[0] in [date_str_1, date_str_2]
    # for event_id  in list(pth.function_crash_history):
    #     assert "ZeroDivisionError" in event_id[2]
    #     assert not "zero_div" in event_id[2]

def test_sqrt(tmpdir):
    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)

    date_str_1 = current_date_gmt_string()

    @idempotent()
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

    date_str_2 = current_date_gmt_string()

    assert len(pth.crash_history) == n-1
    # assert len(pth.function_crash_history) == n - 1
    for event_id in list(pth.crash_history):
        assert "ValueError" in event_id[1]
        assert "my_sqrt" in event_id[1]
        assert event_id[0] in [date_str_1, date_str_2]

    # for event_id in list(pth.function_crash_history):
    #     assert "ValueError" in event_id[2]
    #     assert "my_sqrt" not in event_id[2]