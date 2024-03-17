from pythagoras._01_foundational_objects.value_addresses import ValueAddr
from pythagoras._07_mission_control.global_state_management import (
    initialize, _clean_global_state)
import pythagoras as pth


values_to_test = [1, 10, 10.0, "ten", "10", 10j
    , True, None, [1,2,3],(1,2,3), {1,2,3}, {1:2, None:4, "b": "c"}]

def test_value_address_basic(tmpdir):
    _clean_global_state()
    initialize(tmpdir, n_background_workers = 0)
    counter = 0
    for v in values_to_test:
        assert len(pth.value_store) == counter
        assert ValueAddr(v).get() == v
        assert ValueAddr(v).get() == v
        counter += 1
        assert len(pth.value_store) == counter

    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)
    assert len(pth.value_store) == counter

def test_nested_value_addrs(tmpdir):
    _clean_global_state()
    initialize(tmpdir, n_background_workers=0)
    counter = 0
    for v in values_to_test:
        assert len(pth.value_store) == counter
        assert ValueAddr([ValueAddr(v)]).get()[0].get() == v
        assert ValueAddr([ValueAddr(v)]).get()[0].get() == v
        counter += 2
        assert len(pth.value_store) == counter

    _clean_global_state()
    initialize(tmpdir, n_background_workers = 0)
    assert len(pth.value_store) == counter
