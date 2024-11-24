from pythagoras import BasicPortal
from pythagoras import _PortalTester

def test_portal(tmpdir):

    with _PortalTester():
        portal = BasicPortal(tmpdir)
        description = portal.describe()
        assert description.shape == (2, 3)
        assert description.iloc[0, 2] == str(tmpdir)
        assert description.iloc[1, 2] == "FileDirDict"


