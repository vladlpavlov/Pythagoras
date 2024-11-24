from pythagoras import DataPortal
from pythagoras import _PortalTester
import time

def test_portal(tmpdir):

    with _PortalTester():
        portal = DataPortal(tmpdir)
        description = portal.describe()
        assert description.shape == (6, 3)
        assert description.iloc[4, 2] == 0
        assert description.iloc[5, 2] == 0


def test_stored_values(tmpdir):
    # tmpdir = 25*"Q" +str(int(time.time()))

    with _PortalTester(DataPortal
            , tmpdir
            , p_consistency_checks = 0.5) as t:
        t.portal.value_store["a"] = 100
        t.portal.value_store["b"] = 200
        description = t.portal.describe()
        assert description.shape == (6, 3)
        assert description.iloc[4,2] == 2
        assert description.iloc[5,2] == 0.5







