from pythagoras import PureCodePortal, pure
from pythagoras import _PortalTester
import time

def test_portal(tmpdir):

    with _PortalTester():
        portal = PureCodePortal(tmpdir)
        description = portal.describe()
        assert description.shape == (12, 3)
        assert description.iloc[10, 2] == 0
        assert description.iloc[11, 2] == 0


def f():
    return 1

def g():
    return 2

def test_stored_values(tmpdir):
    # tmpdir = 3*"STORED_VALUES_" +str(int(time.time()))

    global f,g

    with _PortalTester(PureCodePortal
            , tmpdir
            , p_consistency_checks = 0.5) as t:

        f = pure()(f)
        g = pure(island_name="QWERTY")(g)
        f()
        g.swarm()

        description = t.portal.describe()
        assert description.iloc[13, 2] == 1 # Execution results stored
        assert description.iloc[14, 2] == 1 # Queue size










