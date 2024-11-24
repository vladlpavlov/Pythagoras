from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._060_autonomous_functions import *


def f_2():
    return f_1()*10


def f_3():
    return f_2()*10


def f_1():
    return 0


def f_5():
    return f_4()*10


def f_6():
    return f_5()*10


def f_4():
    return 10


def test_two_chains_no_errors(tmpdir):
    with _PortalTester(AutonomousCodePortal, base_dir=tmpdir) as t:

        global f_1, f_2, f_3, f_4, f_5, f_6

        f_2 = autonomous(island_name="Moon")(f_2)
        f_3 = autonomous(island_name="Moon")(f_3)
        f_1 = autonomous(island_name="Moon")(f_1)
        f_5 = autonomous(island_name="Sun")(f_5)
        f_6 = autonomous(island_name="Sun")(f_6)
        f_4 = autonomous(island_name="Sun")(f_4)

        assert f_1() == 0
        assert f_2() == 0
        assert f_3() == 0
        assert f_4() == 10
        assert f_5() == 100
        assert f_6() == 1000