import ast
import sys

import pytest

from pythagoras.NEW_autonomous_functions import analyze_function_dependencies

def sample_from_x_import_y(x):
    from math import sqrt as sq
    from sys import api_version as apv
    from math import fabs
    y = "hehe"
    return [str(i)+y for i in [sq(x),apv,fabs(2)]]
def test_from_x_import_y_s():
    sample_from_x_import_y(3)
    analyzer = analyze_function_dependencies(sample_from_x_import_y)["analyzer"]
    assert analyzer.all_outside_names == {"apv","sq", "str", "fabs"}
    assert analyzer.nonlocal_names == set()
    assert analyzer.imported_global_names == {"apv","sq", "fabs"}
    assert analyzer.imported_packages == {"math", "sys"}
    assert analyzer.local_names == {"i","x","y"}
    assert analyzer.nonimported_outside_names == {"str"}

def sample_import_y_as(a, *args, **kwargs):
    import math
    import sys as s
    b = a + len(args) + len(kwargs)
    x = math.sqrt(math.fabs(b))
    y = s.version
    return str(x) + str(y)

def test_import_y_as():
    sample_import_y_as(3, 4, 5)
    analyzer = analyze_function_dependencies(sample_import_y_as)["analyzer"]
    assert analyzer.all_outside_names == {"len", "math", "str", "s"}
    assert analyzer.nonlocal_names == set()
    assert analyzer.imported_global_names == {"math", "s"}
    assert analyzer.imported_packages == {"math", "sys"}
    assert analyzer.local_names == {"a", "args", "b", "kwargs", "x", "y"}
    assert analyzer.nonimported_outside_names == {"str", "len"}

def sample_good_list_comprecension(x):
    return [i for i in range(x)]

def test_good_list_comprencension():
    sample_good_list_comprecension(3)
    analyzer = analyze_function_dependencies(sample_good_list_comprecension)["analyzer"]
    assert analyzer.all_outside_names == {"range"}
    assert analyzer.nonlocal_names == set()
    assert analyzer.imported_global_names == set()
    assert analyzer.imported_packages == set()
    assert analyzer.local_names == {"i", "x"}
    assert analyzer.nonimported_outside_names == {"range"}

def sample_bad_list_comprecension(x):
    print(i)
    return [i for i in range(x)]

def test_bad_list_comprencension():
    with pytest.raises(Exception):
        sample_bad_list_comprecension(3)
    analyzer = analyze_function_dependencies(sample_bad_list_comprecension)["analyzer"]
    assert analyzer.all_outside_names == {"range","i","print"}
    assert analyzer.nonlocal_names == set()
    assert analyzer.imported_global_names == set()
    assert analyzer.imported_packages == set()
    assert analyzer.local_names == {"x"}
    assert analyzer.nonimported_outside_names == {"range","i","print"}

def sample_for_loop(x):
    for i in range(x):
        print(i)

    for i,y in enumerate(range(x)):
        print(i,y)

def test_for_loop():
    sample_for_loop(3)
    dependencies = analyze_function_dependencies(sample_for_loop)
    analyzer = dependencies["analyzer"]
    assert analyzer.all_outside_names == {"range", "print","enumerate"}
    assert analyzer.nonlocal_names == set()
    assert analyzer.imported_global_names == set()
    assert analyzer.imported_packages == set()
    assert analyzer.local_names == {"i", "x", "y"}
    assert analyzer.nonimported_outside_names == {"range", "print", "enumerate"}
