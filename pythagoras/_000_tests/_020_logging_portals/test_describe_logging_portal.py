from pythagoras import LoggingPortal
from pythagoras import _PortalTester
import time

def test_portal(tmpdir):

    with _PortalTester():
        portal = LoggingPortal(tmpdir)
        description = portal.describe()
        assert description.shape == (4, 3)
        assert description.iloc[2, 2] == 0
        assert description.iloc[3, 2] == 0


def test_exceptions(tmpdir):
    # tmpdir = 25*"Q" +str(int(time.time()))
    try:
        with _PortalTester(LoggingPortal, tmpdir):
            x = 1/0
            print(x)
    except:
        pass

    with _PortalTester(LoggingPortal, tmpdir) as t:
        description = t.portal.describe()
        assert description.shape == (4, 3)
        assert description.iloc[2,2] == 1
        assert description.iloc[3,2] == 1







