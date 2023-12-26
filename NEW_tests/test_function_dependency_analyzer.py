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
    assert analyzer.imported_packages_deep == {"math", "sys"}
    assert analyzer.names.accessible == {"sq", "apv", "x", "y","i", "fabs", "str"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"sq", "apv", "fabs"}
    assert analyzer.names.local == {"sq", "apv", "x", "y","i", "fabs"}
    assert analyzer.names.unclassified_deep == { "str"}

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
    assert analyzer.imported_packages_deep == {"math","sys"}
    assert analyzer.names.accessible == {"a", "args", "kwargs", "math","s","b","x","y","len","str"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"math","s"}
    assert analyzer.names.local == {'kwargs', 'x', 'a', 'args', 'y', 's', 'b', 'math'}
    assert analyzer.names.unclassified_deep == {"len","str"}

def sample_good_list_comprecension(x):
    return [i for i in range(x)]

def test_good_list_comprencension():
    sample_good_list_comprecension(3)
    analyzer = analyze_function_dependencies(sample_good_list_comprecension)["analyzer"]
    assert analyzer.imported_packages_deep == set()
    assert analyzer.names.accessible == {"i", "x", "range"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"i", "x"}
    assert analyzer.names.unclassified_deep == {"range"}


def sample_bad_list_comprecension(x):
    print(i)
    return [i for i in range(x)]

def test_bad_list_comprencension():
    with pytest.raises(Exception):
        sample_bad_list_comprecension(3)
    analyzer = analyze_function_dependencies(sample_bad_list_comprecension)["analyzer"]
    assert analyzer.imported_packages_deep == set()
    assert analyzer.names.accessible == {"i", "x", "range", "print"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"x"}
    assert analyzer.names.unclassified_deep == {"range", "print","i"}

def sample_for_loop(x):
    for i in range(x):
        print(i)

    for i,y in enumerate(range(x)):
        print(i,y)

def test_for_loop():
    sample_for_loop(3)
    dependencies = analyze_function_dependencies(sample_for_loop)
    analyzer = dependencies["analyzer"]
    assert analyzer.imported_packages_deep == set()
    assert analyzer.names.accessible == {"i", "x", "y", "range", "print", "enumerate"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"x", "i", "y"}
    assert analyzer.names.unclassified_deep == {"range", "print", "enumerate"}

def simple_nested(x):
    def nested(y):
        import math
        return math.sqrt(y)
    return nested(x)

def test_simple_nested():
    assert simple_nested(4) == 2
    analyzer = analyze_function_dependencies(simple_nested)["analyzer"]
    assert analyzer.imported_packages_deep == {"math"}
    assert analyzer.names.accessible == {"nested", "x"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"nested", "x"}
    assert analyzer.names.unclassified_deep == set()

def bad_simple_nested(x):
    def nested(y):
        return math.sqrt(y)
    return nested(x)

def test_bad_simple_nested():
    with pytest.raises(Exception):
        bad_simple_nested(4)
    analyzer = analyze_function_dependencies(bad_simple_nested)["analyzer"]
    assert analyzer.imported_packages_deep == set()
    assert analyzer.names.accessible == {"nested", "x"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"nested", "x"}
    assert analyzer.names.unclassified_deep == {"math"}


def simple_nested_2(x):
    import math
    def nested(y):
        return math.sqrt(float(y))
    return nested(x)

def test_simple_nested_2():
    assert simple_nested_2(4) == 2
    analyzer = analyze_function_dependencies(simple_nested_2)["analyzer"]
    assert analyzer.imported_packages_deep == {"math"}
    assert analyzer.names.accessible == {"nested", "x", "math"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"math"}
    assert analyzer.names.local == {"nested", "x", "math"}
    assert analyzer.names.unclassified_deep == {"float"}

def simple_nonlocal(x):
    import math as mmm
    z =12
    def nested(y):
        nonlocal z
        return mmm.sqrt(float(y)+z)
    return nested(x)

def test_simple_nonlocal():
    assert simple_nonlocal(4) == 4
    analyzer = analyze_function_dependencies(simple_nonlocal)["analyzer"]
    assert analyzer.imported_packages_deep == {"math"}
    assert analyzer.names.accessible == {"nested", "x", "z", "mmm"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"mmm"}
    assert analyzer.names.local == {"nested", "x", "z", "mmm"}
    assert analyzer.names.unclassified_deep == {"float"}


def simple_global(x):
    import math as m
    def nested(y):
        nonlocal m
        global float
        return m.sqrt(float(y)+3*int(x))
    return nested(x)

def test_simple_global():
    assert simple_global(4) == 4
    analyzer = analyze_function_dependencies(simple_global)["analyzer"]
    assert analyzer.imported_packages_deep == {"math"}
    assert analyzer.names.accessible == {"nested", "x", "m"}
    assert analyzer.names.explicitly_global_unbound_deep == {"float"}
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"m"}
    assert analyzer.names.local == {"nested", "x", "m"}
    assert analyzer.names.unclassified_deep == {"int"}


def simple_deep(x):
    import math as m
    def nested(y):
        import ast as a
        y2=y
        def subnested(z):
            global print
            nonlocal m
            return str(z+y2)
        global float
        return subnested
    def second_nested(i):
        from pandas import DataFrame
        DataFrame()
        return i*i
    return nested(x)(x)

def test_simple_deep():
    assert simple_deep(4) == "8"
    analyzer = analyze_function_dependencies(simple_deep)
    tree = analyzer["tree"]
    analyzer = analyzer["analyzer"]
    assert analyzer.imported_packages_deep == {"math","ast", "pandas"}
    assert analyzer.names.accessible == {"nested","second_nested", "x", "m"}
    assert analyzer.names.explicitly_global_unbound_deep == {"float","print"}
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"m"}
    assert analyzer.names.local == {"nested","second_nested", "x", "m"}
    assert analyzer.names.unclassified_deep == {"str"}

def nested_yeld(x):
    import math as m
    def nested(y):
        import ast as a
        y2=y
        def subnested(z):
            global print
            nonlocal m
            yield str(z+y2)
        global float
        return subnested
    def second_nested(i):
        from pandas import DataFrame
        DataFrame()
        return i*i
    return nested(x)(x)

def test_nested_yeld():
    analyzer = analyze_function_dependencies(simple_deep)
    tree = analyzer["tree"]
    analyzer = analyzer["analyzer"]
    assert analyzer.n_yelds == 0

def simple_yeld(x):
    y = x+2
    if y > 100:
        yield y
    else:
        yield x

def test_simple_yeld():
    analyzer = analyze_function_dependencies(simple_yeld)
    tree = analyzer["tree"]
    analyzer = analyzer["analyzer"]
    assert analyzer.n_yelds == 2



