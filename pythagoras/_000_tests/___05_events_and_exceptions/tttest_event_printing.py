import pytest

import pythagoras as pth

from pythagoras.___07_mission_control.global_state_management import (
    _force_initialize,_clean_global_state)
from pythagoras.___OLD_05_events_and_exceptions.event_posters import (
    print_event)


def test_outside_a_function(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):
        pth.print_event()
        pth.print_event("hello")
        assert len(pth.default_portal.event_log) == 2
        pth.print_event(msg = "one more")
        assert len(pth.default_portal.event_log) == 3

def test_labeled_outside_a_function(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):
        for i in range(3):
            print_event["QWERTYTREWQ"]("qwertytrewq", mmm="MMM test_event")
        assert len(pth.default_portal.event_log) == 3
        for e in pth.default_portal.event_log:
            assert "QWERTYTREWQ" in e[1]

def test_no_initialization():
    _clean_global_state()
    with pytest.raises(AssertionError):
        print_event()
    with pytest.raises(AssertionError):
        print_event["test_event"]()

def test_inside_an_idempotent_function(tmpdir):
    # tmpdir = "P_P_P_P_P_P_P_P_P_P_P_P_P_P_P_P_P_P_P_P"
    with _force_initialize(tmpdir, n_background_workers=0):
        @pth.idempotent()
        def some_function():
            print_event("Hello", "how are you?")
            print_event(m="test_event")
            pth.print_event["MountainView"]("California",m="another_test_event")

        assert len(pth.default_portal.event_log) == 0
        assert len(some_function.get_address().events) == 0
        some_function()
        assert len(pth.default_portal.event_log) == 3
        assert len(some_function.get_address().events) == 3





