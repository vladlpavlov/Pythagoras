import pytest

from persidict import FileDirDict

from pythagoras._02_ordinary_functions.ordinary_decorator import ordinary
from pythagoras._03_autonomous_functions.autonomous_decorators import autonomous
from pythagoras._04_idempotent_functions.idempotent_decorator import idempotent
from pythagoras._04_idempotent_functions.idempotency_checks import is_idempotent
from pythagoras._07_mission_control.global_state_management import (
    _clean_global_state, _force_initialize)

import pythagoras as pth



def test_basics(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):

        @idempotent()
        def f():
            return 1

        assert f() == 1
        a = f.get_address()
        assert a.ready
        assert a.get() == 1
        assert len(a.execution_attempts) == 1
        assert len(a.execution_results) == 1
        assert len(a.execution_records) == 1
        assert a.execution_records[0].result == 1
        assert isinstance(a.execution_records[0].attempt_context, dict)
        assert a.execution_records[0].events == []
        assert a.execution_records[0].crashes == []
        assert a.execution_records[0].output == ""


def test_exception(tmpdir):
    with _force_initialize(tmpdir, n_background_workers=0):

        @idempotent()
        def f():
            return 1/0

        with pytest.raises(ZeroDivisionError):
            f()
        a = f.get_address()
        assert not a.ready
        assert len(a.execution_attempts) == 1
        assert len(a.execution_results) == 0
        assert len(a.execution_records) == 1
        assert isinstance(a.execution_records[0].attempt_context, dict)
        assert a.execution_records[0].events == []
        assert len(a.execution_records[0].crashes) == 1
        with pytest.raises(Exception):
            x = a.execution_records[0].result
