from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, initialize, _force_initialize)
import pythagoras as pth



def simple_func(n: int) -> int:
    return 10 * n


def complex_func(n: int) -> int:
    return simple_func(n=n)

def test_addrr_execute(tmpdir):
    # tmpdir = "TTTTTTTTTTTTTTTTTTTTT"

    with _force_initialize(tmpdir, n_background_workers=0):

        global simple_func, complex_func
        simple_func = pth.idempotent()(simple_func)
        complex_func = pth.idempotent()(complex_func)

        addr_10 = complex_func.get_address(n=0)

        _clean_global_state()
        initialize(tmpdir, n_background_workers=0)

        addr_10._invalidate_cache()
        assert addr_10.execute() == 0

        addr_10._invalidate_cache()
        assert addr_10.function(n=1) == 10

