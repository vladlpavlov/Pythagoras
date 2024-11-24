from pythagoras import AutonomousCodePortal, _PortalTester
from pythagoras._070_pure_functions.process_augmented_func_src import (
    process_augmented_func_src)


src_1_good ="""
@pth.autonomous(island_name=None)
def f_1_1():
    pass
    
@pth.strictly_autonomous()
def f_1_2():
    pass
"""


def test_strictly_autonomous_func_registration(tmpdir):
    with _PortalTester(AutonomousCodePortal, tmpdir) as t:
        portal = t.portal

        assert len(portal.known_functions) == 1

        for _ in range(5):
            process_augmented_func_src(src_1_good)
            assert len(portal.known_functions) == 1
            assert len(portal.known_functions[portal.default_island_name]) == 2
