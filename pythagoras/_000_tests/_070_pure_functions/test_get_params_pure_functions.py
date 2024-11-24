from persidict import FileDirDict

from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal)

def test_get_params_1(tmpdir):
    dir = str(tmpdir)
    portal = PureCodePortal(base_dir=tmpdir)
    params = portal.get_params()
    assert params["base_dir"] == dir
    assert params["dict_type"] == FileDirDict
    assert params["default_island_name"] == "Samos"
    assert params["p_consistency_checks"] == 0
    assert len(params) == 4

def test_get_params_2(tmpdir):
    dir = str(tmpdir)
    portal = PureCodePortal(base_dir=tmpdir
        , default_island_name= "QWERTY"
        , dict_type=FileDirDict
        , p_consistency_checks=1)
    params = portal.get_params()
    assert params["base_dir"] == dir
    assert params["dict_type"] == FileDirDict
    assert params["default_island_name"] == "QWERTY"
    assert params["p_consistency_checks"] == 1
    assert len(params) == 4

