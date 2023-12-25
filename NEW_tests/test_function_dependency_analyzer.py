import ast
import sys

from pythagoras.NEW_autonomous_functions import analyze_function_dependencies

def from_x_import_y(x):
    from math import sqrt as sq
    from sys import api_version as apv
    from math import fabs
    y = "hehe"
    return [str(i)+y for i in [sq(x),apv,fabs(2)]]
def test_from_x_import_y_s():
    from_x_import_y(3)
    analyzer = analyze_function_dependencies(from_x_import_y)
    assert analyzer.all_outside_names == {"apv","sq", "str", "fabs"}
    assert analyzer.nonlocal_names == set()
    assert analyzer.imported_global_names == {"apv","sq", "fabs"}
    assert analyzer.imported_packages == {"math", "sys"}
    assert analyzer.local_names == {"i","x","y"}
    assert analyzer.nonimported_outside_names == {"str"}

def import_y_as(a, *args, **kwargs):
    import math
    import sys as s
    b = a + len(args) + len(kwargs)
    x = math.sqrt(math.fabs(b))
    y = s.version
    return str(x) + str(y)

def test_import_y_as():
    import_y_as(3,4,5)
    analyzer = analyze_function_dependencies(import_y_as)
    assert analyzer.all_outside_names == {"len", "math", "str", "s"}
    assert analyzer.nonlocal_names == set()
    assert analyzer.imported_global_names == {"math", "s"}
    assert analyzer.imported_packages == {"math", "sys"}
    assert analyzer.local_names == {"a", "args", "b", "kwargs", "x", "y"}
    assert analyzer.nonimported_outside_names == {"str", "len"}
