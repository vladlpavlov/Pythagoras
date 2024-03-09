from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state)

import pythagoras as pth

def test_initialization(tmpdir):
    _clean_global_state()
    pth.initialize(
        base_dir = tmpdir
        , n_background_workers = 3
        )
    