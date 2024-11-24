from persidict import FileDirDict

from pythagoras._030_data_portals.data_portals import (
    DataPortal)

def test_get_params_1(tmpdir):
    dir = str(tmpdir)
    portal = DataPortal(base_dir=tmpdir, p_consistency_checks=0.5)
    params = portal.get_params()
    assert params["base_dir"] == dir
    assert params["dict_type"] == FileDirDict
    assert params["p_consistency_checks"] is 0.5
    assert len(params) == 3

def test_get_params_2(tmpdir):
    dir = str(tmpdir)
    portal = DataPortal(base_dir=tmpdir, dict_type=FileDirDict)
    params = portal.get_params()
    assert params["base_dir"] == dir
    assert params["dict_type"] == FileDirDict
    assert params["p_consistency_checks"] == 0
    assert len(params) == 3

