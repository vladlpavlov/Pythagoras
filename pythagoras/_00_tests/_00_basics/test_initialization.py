from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state)
import pythagoras as pth

def test_initialization(tmpdir):
    _clean_global_state()
    pth.initialize(
        base_dir = tmpdir
        , cloud_type = "local"
        , n_background_workers=0
        , default_island_name = "default"
        )
