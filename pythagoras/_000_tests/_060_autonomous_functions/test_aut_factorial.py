from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._060_autonomous_functions import *


def factorial(n:int) -> int:
    if n in [0, 1]:
        return 1
    else:
        return n * factorial(n=n-1)

def test_aut_factorial(tmpdir):
    with _PortalTester(AutonomousCodePortal, root_dict=tmpdir):
        global factorial
        factorial = autonomous()(factorial)
        assert factorial(n=5) == 120