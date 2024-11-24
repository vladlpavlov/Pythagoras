from pythagoras._070_pure_functions.process_augmented_func_src import (
    process_augmented_func_src)
from pythagoras import _PortalTester, AutonomousCodePortal

src_1_good ="""
@pth.autonomous(island_name='DEMO')
def f_1_1():
    pass
    
@pth.autonomous()
def f_1_2():
    pass
"""

def test_basic_func_registration(tmpdir):
    with _PortalTester(AutonomousCodePortal, tmpdir) as t:
        portal = t.portal
        assert len(portal.known_functions) == 1
        assert len(portal.known_functions[
                       portal.default_island_name]) == 0

        for _ in range(5):
            process_augmented_func_src(src_1_good)
            assert len(portal.known_functions) == 2
            assert len(portal.known_functions["DEMO"]) == 1
            assert len(portal.known_functions[
                portal.default_island_name]) == 1