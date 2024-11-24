from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal,PureFnExecutionResultAddr)
from pythagoras._070_pure_functions.pure_decorator import pure
from pythagoras._070_pure_functions.purity_checks import is_pure


def f_before(**kwargs):
    return sum(kwargs.values())

def test_basics(tmpdir):
    with _PortalTester(PureCodePortal, tmpdir) as t:

        f_after = pure()(f_before)

        args_dict = dict()
        for i in range(10):
            arg_name = f"arg_{i}"
            args_dict[arg_name] = i
            assert f_after(**args_dict) == f_before(**args_dict)
