import pytest

from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._820_strings_signatures_converters.current_date_gmt_str import current_date_gmt_string
from pythagoras._060_autonomous_functions import *



def test_sqrt(tmpdir):

    with _PortalTester(AutonomousCodePortal, root_dict=tmpdir) as t:

        @autonomous()
        def my_sqrt(x: float) -> float:
            from math import sqrt
            return sqrt(x)

        date_str_1 = current_date_gmt_string()

        n = 5
        for i in range(-10, n):
            if i <= 0:
                my_sqrt(x=-i)
                continue
            with pytest.raises(ValueError):
                my_sqrt(x=-i)

        date_str_2 = current_date_gmt_string()

        assert len(t.portal.crash_history) == (n - 1)*2
        for event_id in list(t.portal.crash_history):
            # assert "ValueError" in event_id[1]
            # assert "my_sqrt" in event_id[1]
            # assert event_id[0] in [date_str_1, date_str_2]
            pass