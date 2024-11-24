from pythagoras._010_basic_portals.portal_tester import _PortalTester
from pythagoras._060_autonomous_functions import *

import pytest


def test_2_didderent_functions_same_name(tmpdir):
    with _PortalTester(AutonomousCodePortal, base_dir=tmpdir):
        def f():
            return 1
        f_1 = autonomous(island_name="Moon")(f)
        f_2 = autonomous(island_name="Sun")(f)
        f_10 = strictly_autonomous()(f)

        assert f_1() == 1

        def f():
            return 2

        f_3 = autonomous(island_name="Earth")(f)
        with pytest.raises(Exception):
            f_4 = autonomous(island_name="Moon")(f)
        with pytest.raises(Exception):
            f_20 = strictly_autonomous()(f)

def test_2_similar_functions_same_name(tmpdir):
    with _PortalTester(AutonomousCodePortal, base_dir=tmpdir):
        def f():
            return 100
        f_1 = autonomous(island_name="Moon")(f)
        f_2 = autonomous(island_name="Sun")(f)
        f_10 = strictly_autonomous()(f)

        def f():
            """ This is a function """
            return 100 # This is a comment

        f_3 = autonomous(island_name="Earth")(f)
        f_4 = autonomous(island_name="Moon")(f)
        f_20 = strictly_autonomous()(f)

        assert f_1() == 100
        assert f_2() == 100
        assert f_3() == 100
        assert f_4() == 100
        assert f_10() == 100
        assert f_20() == 100

