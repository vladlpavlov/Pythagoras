from persidict import FileDirDict

from pythagoras._090_swarming_portals.swarming_portals import (
    SwarmingPortal)

def test_get_params_1(tmpdir):
    dir = str(tmpdir)
    portal = SwarmingPortal(
        base_dir=tmpdir
        , n_background_workers=5)
    params = portal.get_params()
    assert params["n_background_workers"] == 5
    assert params["runtime_id"] == portal.runtime_id
    assert params["base_dir"] == dir
    assert params["dict_type"] == FileDirDict
    assert params["default_island_name"] == "Samos"
    assert params["p_consistency_checks"] == 0
    assert len(params) == 6

def test_get_params_2(tmpdir):
    dir = str(tmpdir)
    portal = SwarmingPortal(base_dir=tmpdir
                            , n_background_workers=0
                            , default_island_name="QWERTY"
                            , p_consistency_checks=0
                            , dict_type=FileDirDict)
    params = portal.get_params()
    assert params["n_background_workers"] == 0
    assert params["runtime_id"] == portal.runtime_id
    assert params["base_dir"] == dir
    assert params["dict_type"] == FileDirDict
    assert params["default_island_name"] == "QWERTY"
    assert params["p_consistency_checks"] == 0
    assert len(params) == 6

