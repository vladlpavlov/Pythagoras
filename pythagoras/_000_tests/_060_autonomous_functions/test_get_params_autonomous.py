from persidict import FileDirDict

from pythagoras._060_autonomous_functions.autonomous_core_classes import (
    AutonomousCodePortal)

def test_get_params_1(tmpdir):
    dir = str(tmpdir)
    portal = AutonomousCodePortal(base_dir=tmpdir)
    params = portal.get_params()
    assert params["base_dir"] == dir
    assert params["dict_type"] == FileDirDict
    assert params["default_island_name"] == "Samos"
    assert params["p_consistency_checks"] == 0
    assert len(params) == 4

def test_get_params_2(tmpdir):
    dir = str(tmpdir)
    portal = AutonomousCodePortal(base_dir=tmpdir
        , default_island_name= "QWERTY"
        , dict_type=FileDirDict)
    params = portal.get_params()
    assert params["base_dir"] == dir
    assert params["dict_type"] == FileDirDict
    assert params["default_island_name"] == "QWERTY"
    assert params["p_consistency_checks"] == 0
    assert len(params) == 4

