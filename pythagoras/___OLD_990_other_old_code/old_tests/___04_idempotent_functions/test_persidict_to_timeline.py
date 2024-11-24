from persidict import FileDirDict
from pythagoras.___04_idempotent_functions.persidict_to_timeline import (
    build_timeline_from_persidict)


def test_timelimne_builder(tmpdir):
    d = FileDirDict(tmpdir)
    d["a"] = 1
    d["b"] = 45
    d["c"] = 10
    d["d"] = -56
    d["e"] = 2
    d["b"] = 100
    d["d"] = 1000
    d["e"] = 10000
    tl = build_timeline_from_persidict(d)
    assert tl == [1,10,100,1000,10000]

def test_empty_timeline_(tmpdir):
    d = FileDirDict(tmpdir)
    tl = build_timeline_from_persidict(d)
    assert tl == []

