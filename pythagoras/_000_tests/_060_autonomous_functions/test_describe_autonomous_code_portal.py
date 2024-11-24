from pythagoras import AutonomousCodePortal, autonomous
from pythagoras import _PortalTester
import time

def test_portal(tmpdir):

    with _PortalTester():
        portal = AutonomousCodePortal(tmpdir)
        description = portal.describe()
        assert description.shape == (10, 3)
        assert description.iloc[6, 2] == 1 # Number of islands
        assert description.iloc[7, 2] == "Samos"
        assert description.iloc[8, 2] == "Samos"
        assert description.iloc[9, 2] == 0


def f():
    return 1

def g():
    return 2

def test_stored_values(tmpdir):
    # tmpdir = 25*"Q" +str(int(time.time()))

    global f,g

    with _PortalTester(AutonomousCodePortal
            , tmpdir
            , p_consistency_checks = 0.5) as t:

        f = autonomous()(f)
        g = autonomous(island_name="QWERTY")(g)

        description = t.portal.describe()
        assert description.shape == (13, 3)
        assert description.iloc[6, 2] == 2  # Number of islands
        assert description.iloc[7, 2] == "Samos"
        assert description.iloc[8, 2] == "Samos, QWERTY"
        assert description.iloc[9, 2] == 1
        assert description.iloc[10, 2] == "f"
        assert description.iloc[11, 2] == 1
        assert description.iloc[12, 2] == "g"










