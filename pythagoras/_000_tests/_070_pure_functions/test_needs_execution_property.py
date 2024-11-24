from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
import pytest


def factorial(n:int) -> int:
    if n in [0, 1]:
        return 1
    else:
        return n * factorial(n=n-1)

def test_needs_execution(tmpdir):

    with _PortalTester(PureCodePortal, tmpdir) as t:
    # initialize(base_dir="TTTTTTTTTTTTTTTTTTTTT")

        global factorial
        factorial = pure()(factorial)

        addr = PureFnExecutionResultAddr(a_fn=factorial, arguments=dict(n=5))

        assert not addr.ready
        assert addr.can_be_executed
        assert addr.needs_execution
        assert len(addr.execution_attempts) == 0
        addr.request_execution()
        assert addr.execution_requested

        factorial(n=5)
        assert addr.ready
        assert addr.can_be_executed
        assert not addr.needs_execution
        assert len(addr.execution_attempts) == 1
        assert not addr.execution_requested

        factorial(n=5)
        assert addr.ready
        assert addr.can_be_executed
        assert not addr.needs_execution
        assert len(addr.execution_attempts) == 1
        assert not addr.execution_requested



