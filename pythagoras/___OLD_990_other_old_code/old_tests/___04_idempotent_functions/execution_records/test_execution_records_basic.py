from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
import pytest

def test_basics(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        @pure()
        def f():
            return 1

        assert f() == 1
        a = f.get_address()
        assert a.ready
        assert a.get() == 1
        assert len(a.execution_attempts) == 1
        assert len(a.execution_results) == 1
        assert len(a.execution_records) == 1
        all_records = a.execution_records
        first_record = all_records[0]
        assert first_record.result == 1
        assert isinstance(a.execution_records[0].attempt_context, dict)
        assert a.execution_records[0].events == []
        assert a.execution_records[0].crashes == []
        assert a.execution_records[0].output == ""


def test_exception(tmpdir):
    # tmpdir = "UOUOUOUOUOUOUOUOUOUOUOUOUOUOUOUO"
    with _PortalTester(PureCodePortal, tmpdir) as t:

        @pure()
        def fff():
            return 1/0

        with pytest.raises(ZeroDivisionError):
            fff()
        a = fff.get_address()
        assert not a.ready
        assert len(a.execution_attempts) == 1
        assert len(a.execution_results) == 0
        assert len(a.execution_records) == 1
        assert isinstance(a.execution_records[0].attempt_context, dict)
        assert a.execution_records[0].events == []
        assert len(a.execution_records[0].crashes) == 1
        with pytest.raises(Exception):
            x = a.execution_records[0].result
        assert "ZeroDivisionError" in a.execution_records[0].output
