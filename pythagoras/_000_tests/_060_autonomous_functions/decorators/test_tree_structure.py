from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._060_autonomous_functions import *


def f_1():
    return 0


def f_2():
    return 0


def f_3():
    return 0


def f_4():
    return 0


def f_5():
    return 0


def f_6():
    return 0


def f_1_2():
    return f_1() + f_2()


def f_2_3():
    return f_2() + f_3()


def f_3_4():
    return f_3() + f_4()


def f_4_5():
    return f_4() + f_5()


def f_5_6():
    return f_5() + f_6()


def f_1_2_3():
    return f_1_2() + f_2_3()


def f_2_3_4():
    return f_2_3() + f_3_4()


def f_3_4_5():
    return f_3_4() + f_4_5()


def f_4_5_6():
    return f_4_5() + f_5_6()


def total():
    return f_1_2_3() + f_2_3_4() + f_3_4_5() + f_4_5_6()


def test_tree(tmpdir):
    with _PortalTester(AutonomousCodePortal, root_dict=tmpdir) as t:

        global f_1, f_2, f_3, f_4, f_5, f_6, f_1_2, f_2_3
        global f_3_4, f_4_5, f_5_6, f_1_2_3, f_2_3_4, f_3_4_5
        global f_4_5_6, total

        f_1 = autonomous("kuku")(f_1)
        f_2 = autonomous("kuku")(f_2)
        f_3 = autonomous("kuku")(f_3)
        f_4 = autonomous("kuku")(f_4)
        f_5 = autonomous("kuku")(f_5)
        f_6 = autonomous("kuku")(f_6)
        f_1_2 = autonomous("kuku")(f_1_2)
        f_2_3 = autonomous("kuku")(f_2_3)
        f_3_4 = autonomous("kuku")(f_3_4)
        f_4_5 = autonomous("kuku")(f_4_5)
        f_5_6 = autonomous("kuku")(f_5_6)
        f_1_2_3 = autonomous("kuku")(f_1_2_3)
        f_2_3_4 = autonomous("kuku")(f_2_3_4)
        f_3_4_5 = autonomous("kuku")(f_3_4_5)
        f_4_5_6 = autonomous("kuku")(f_4_5_6)
        total = autonomous("kuku")(total)

        assert total() == 0

