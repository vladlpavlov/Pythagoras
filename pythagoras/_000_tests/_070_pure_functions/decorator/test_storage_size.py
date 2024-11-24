from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
from pythagoras._070_pure_functions.purity_checks import is_pure



def test_no_args(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        assert len(t.portal.value_store) == 0
        @pure()
        def f():
            return 0

        assert f() == 0
        assert len(t.portal.execution_results) == 1
        assert len(t.portal.value_store) == 4

def test_two_args(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        assert len(t.portal.value_store) == 0

        @pure()
        def f_sum(x,y):
            return x+y

        assert f_sum(x=0,y=0) == 0
        assert len(t.portal.execution_results) == 1
        assert len(t.portal.value_store) == 4

        assert f_sum(x=2, y=3) == 5
        assert len(t.portal.execution_results) == 2
        assert len(t.portal.value_store) == 9