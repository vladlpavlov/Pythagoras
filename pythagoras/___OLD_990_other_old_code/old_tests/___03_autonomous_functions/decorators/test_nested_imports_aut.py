from pythagoras.___03_OLD_autonomous_functions import autonomous
from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize)


def test_nested_from_import(tmpdir):
    with _force_initialize(base_dir=tmpdir, n_background_workers=0):

        @autonomous()
        def f(x:float)->float:
            from math import sqrt
            return sqrt(x)

        assert f(x=4) == 2


def test_nested_import_as(tmpdir):
    with _force_initialize(base_dir=tmpdir,n_background_workers=0):

        @autonomous()
        def f(x:float)->float:
            import math as mm
            return mm.sin(x)

        assert f(x=0) == 0

def test_nested_from_import_as(tmpdir):
    with _force_initialize(base_dir=tmpdir,n_background_workers=0):

        @autonomous()
        def f(x:float)->float:
            from math import log as l
            return l(x)

        assert f(x=1) == 0

