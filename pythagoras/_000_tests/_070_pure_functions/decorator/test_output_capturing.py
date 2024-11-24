from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
from pythagoras._070_pure_functions.purity_checks import is_pure


def test_print(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        @pure()
        def f(n:int):
            print(f"<{n}>")

        for i in range(1,7):
            f(n=i)
            f(n=i)
            assert (len(t.portal.run_history.txt) == i)