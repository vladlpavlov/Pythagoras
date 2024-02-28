import pytest

import pythagoras as pth
from pythagoras._05_mission_control.global_state_management import (
    _clean_global_state)

def test_init_checks(tmpdir):
    _clean_global_state()
    def f_1():
        pass

    def f_2():
        pass

    with pytest.raises(AssertionError):
        pth.autonomous()(f_1)

    pth.autonomous(require_pth=False)(f_2)

    _clean_global_state()
    pth.initialize(base_dir=tmpdir)

    pth.autonomous()(f_1)
    pth.autonomous()(f_2)

