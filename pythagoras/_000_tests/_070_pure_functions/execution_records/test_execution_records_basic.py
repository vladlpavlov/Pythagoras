import time

from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
import pytest

def test_basics(tmpdir):
    # tmpdir = 3*"BASICS_EXECUTION_RECORDS_" +str(int(time.time()))
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


def test_basics_many_kwargs(tmpdir):
    # tmpdir = 3*"BASICS_MANY_KWARGS_" +str(int(time.time()))
    with _PortalTester(PureCodePortal, tmpdir) as t:

        @pure()
        def f(**kwargs):
            print(f"{kwargs=}")
            result = sum(kwargs.values())
            print(f"{result=}")
            return result

        total = 0
        all_args = dict()
        for i in range(1,11):
            total += i
            all_args["a"+str(i)] = i
            assert f(**all_args) == total
            a = f.get_address(**all_args)
            assert a.ready
            for j in range(1,5):
                assert a.get() == total
            assert len(a.execution_attempts) == 1
            assert len(a.execution_results) == 1
            assert len(a.execution_records) == 1
            all_records = a.execution_records
            last_record = all_records[-1]
            assert last_record.result == total
            assert isinstance(last_record.attempt_context, dict)
            assert last_record.events == []
            assert last_record.crashes == []
            assert isinstance(last_record.output, str)
            assert "kwargs" in last_record.output
            assert "result" in last_record.output

            assert len(t.portal.execution_results) == i
            assert len(t.portal.crash_history) == 0
            assert len(t.portal.execution_requests) == 0



def test_total_recalc(tmpdir):
    # tmpdir = 5*"TOTAL_RECALC_" +str(int(time.time()))
    with _PortalTester(
            PureCodePortal
            , tmpdir
            , p_consistency_checks = 1
            ) as t:

        @pure()
        def f():
            return 1
        NUM_ITERS = 5

        for i in range(NUM_ITERS):
            assert f() == 1

        a = f.get_address()
        assert a.ready
        assert a.get() == 1

        assert len(a.execution_attempts) == NUM_ITERS
        assert len(a.execution_results) == NUM_ITERS
        assert len(a.execution_records) == NUM_ITERS
        all_records = a.execution_records
        first_record = all_records[0]
        assert first_record.result == 1
        assert isinstance(a.execution_records[0].attempt_context, dict)
        assert a.execution_records[0].events == []
        assert a.execution_records[0].crashes == []
        assert a.execution_records[0].output == ""


def test_exception(tmpdir):
    # tmpdir = 3*"EXCEPTIONS_" +str(int(time.time()))
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
        # assert a.execution_records[0].events == []
        # assert len(a.execution_records[0].crashes) == 1
        with pytest.raises(Exception):
            x = a.execution_records[0].result
        assert "ZeroDivisionError" in a.execution_records[0].output
