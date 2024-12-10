from pythagoras import SwarmingPortal, pure
from pythagoras import _PortalTester


def test_portal(tmpdir):

    with _PortalTester():
        portal = SwarmingPortal(
            root_dict=tmpdir,
            n_background_workers=2)
        description = portal.describe()
        assert description.shape == (13, 3)
        assert description.iloc[12, 2] == 2







