from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._820_strings_signatures_converters.current_date_gmt_str import (
    current_date_gmt_string)
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal)
from pythagoras._070_pure_functions.pure_decorator import pure
import pytest


def test_zero_div(tmpdir):
    # tmpdir=5*"ZERO_DIV_"+str(int(time.time()))
    with _PortalTester(PureCodePortal, tmpdir) as t:
        catch_all = t.portal.crash_history.get_subdict("__CATCH_ALL__")
        assert len(catch_all) == 0
        date_str_1 = current_date_gmt_string()

        @pure()
        def zero_div(x:float)->float:
            return x/0

        with pytest.raises(ZeroDivisionError):
            zero_div(x=2024)

        date_str_2 = current_date_gmt_string()

        assert len(catch_all) >= 1
        for event_id  in list(catch_all):
            assert "ZeroDivisionError" in event_id[1]
            assert event_id[0] in [date_str_1, date_str_2]
        # for event_id  in list(pth.function_crash_history):
        #     assert "ZeroDivisionError" in event_id[2]
        #     assert not "zero_div" in event_id[2]

# def test_sqrt(tmpdir):
#     with _force_initialize(tmpdir, n_background_workers=0):
#
#         date_str_1 = current_date_gmt_string()
#
#         @idempotent()
#         def my_sqrt(x: float) -> float:
#             from math import sqrt
#             return sqrt(x)
#
#         n = 5
#         for i in range(n):
#             if i <= 0:
#                 my_sqrt(x=-i)
#                 continue
#             with pytest.raises(ValueError):
#                 my_sqrt(x=-i)
#
#         date_str_2 = current_date_gmt_string()
#
#         assert len(pth.default_portal.crash_history) == n-1
#         for event_id in list(pth.default_portal.crash_history):
#             assert "ValueError" in event_id[1]
#             assert "my_sqrt" in event_id[1]
#             assert event_id[0] in [date_str_1, date_str_2]
#
#         # for event_id in list(pth.function_crash_history):
#         #     assert "ValueError" in event_id[2]
#         #     assert "my_sqrt" not in event_id[2]