from pythagoras._03_autonomous_functions import autonomous
from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state, initialize)


def test_nested_from_import(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    @autonomous()
    def f(x:float)->float:
        from math import sqrt
        return sqrt(x)

    assert f(x=4) == 2


def test_nested_import_as(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    @autonomous()
    def f(x:float)->float:
        import math as mm
        return mm.sin(x)

    assert f(x=0) == 0

def test_nested_from_import_as(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir)

    @autonomous()
    def f(x:float)->float:
        from math import log as l
        return l(x)

    assert f(x=1) == 0

