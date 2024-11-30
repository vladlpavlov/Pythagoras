
import pythagoras as pth


def test_initialize(tmpdir): # TODO: refactor
    x = pth.initialize(base_dir=tmpdir)
    assert isinstance(x, pth.pd.DataFrame)
