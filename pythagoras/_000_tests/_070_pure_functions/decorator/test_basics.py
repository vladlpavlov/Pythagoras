from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
from pythagoras._070_pure_functions.purity_checks import is_pure


def test_basics(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:
        def f_ab(a, b):
            return a + b

        result = f_ab(a=1,b=2)
        assert not is_pure(f_ab)
        f_1 = pure()(f_ab)
        #
        assert is_pure(f_1)
        for i in range(3):
            assert f_1(a=1,b=2) == result