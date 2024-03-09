"""Test package_dependencies.py."""

from pythagoras.________OLD________.OLD_package_dependencies import *

def test_PckgDependencies_basic():
    p_dep_1 = PckgDependencies(["pythagoras~=1.0", "pandas", "numpy==1.24"])
    p_dep_2 = PckgDependencies([["pandas"]], numpy=1.24, pythagoras="~=1.0")

    p_dep_3 = PckgDependencies("""pandas
        pythagoras~=1.0
        numpy==1.24
        """
        )

    p_dep_4 = PckgDependencies()
    p_dep_4["numpy"] = 1.24
    p_dep_4["pythagoras"] = "~=1.0"
    p_dep_4 += "pandas"

    assert len(p_dep_1) == len(p_dep_2) == len(p_dep_3) == 3
    assert p_dep_1 == p_dep_2 == p_dep_3 == p_dep_4

    del p_dep_4["numpy"]
    assert len(p_dep_4) == 2