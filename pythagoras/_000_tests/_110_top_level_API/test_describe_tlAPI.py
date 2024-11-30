from pythagoras import _PortalTester, SwarmingPortal
import pythagoras as pth


def test_describe(tmpdir): # TODO: refactor
    with _PortalTester(SwarmingPortal
        , tmpdir, n_background_workers=0) as t:

        description = pth.describe()
        assert isinstance(description, pth.pd.DataFrame)

