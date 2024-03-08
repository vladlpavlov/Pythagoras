import pytest

import pythagoras as pth

from pythagoras._06_mission_control.global_state_management import (
    _clean_global_state)
from pythagoras._05_events_and_exceptions.event_poster import (
    post_event)


def test_outside_a_function(tmpdir):
    _clean_global_state()
    pth.initialize(tmpdir)
    pth.post_event()
    assert len(pth.event_log) == 1
    pth.post_event(msg = "one more")
    assert len(pth.event_log) == 2

def test_labeled_outside_a_function(tmpdir):
    _clean_global_state()
    pth.initialize(tmpdir)
    for i in range(3):
        post_event["QWERTYTREWQ"]()
    assert len(pth.event_log) == 3
    for e in pth.event_log:
        assert "QWERTYTREWQ" in e[1]

def test_no_initialization():
    _clean_global_state()
    with pytest.raises(AssertionError):
        post_event()
    with pytest.raises(AssertionError):
        post_event["test_event"]()

def test_inside_an_idempotent_function(tmpdir):
    _clean_global_state()
    pth.initialize(tmpdir)
    @pth.idempotent()
    def some_function():
        post_event(m="test_event")
        pth.post_event["MountainView"](m="another_test_event")

    assert len(pth.event_log) == 0
    assert len(some_function.get_address().events) == 0
    some_function()
    assert len(pth.event_log) == 2
    assert len(some_function.get_address().events) == 2





