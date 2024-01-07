import ast
import sys

import pytest

from pythagoras.python_utils.names_usage_analyzer import *

def sample_from_x_import_y(x):
    from math import sqrt as sq
    from sys import api_version as apv
    from math import fabs
    y = "hehe"
    return [str(i)+y for i in [sq(x),apv,fabs(2)]]
def test_from_x_import_y_s():
    sample_from_x_import_y(3)
    analyzer = analyze_names_in_function(sample_from_x_import_y)["analyzer"]
    assert analyzer.imported_packages_deep == {"math", "sys"}
    assert analyzer.names.accessible == {"sq", "apv", "x", "y","i", "fabs", "str"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"sq", "apv", "fabs"}
    assert analyzer.names.local == {"x", "y","i"}
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
    analyzer = analyze_names_in_function(sample_import_y_as)["analyzer"]
    assert analyzer.names.function == "sample_import_y_as"
    assert analyzer.imported_packages_deep == {"math","sys"}
    assert analyzer.names.accessible == {"a", "args", "kwargs", "math","s","b","x","y","len","str"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"math","s"}
    assert analyzer.names.local == {'kwargs', 'x', 'a', 'args', 'y', 'b'}
    assert analyzer.names.unclassified_deep == {"len","str"}

def sample_good_list_comprecension(x):
    return [i for i in range(x)]

def test_good_list_comprencension():
    sample_good_list_comprecension(3)
    analyzer = analyze_names_in_function(sample_good_list_comprecension)["analyzer"]
    assert analyzer.imported_packages_deep == set()
    assert analyzer.names.accessible == {"i", "x", "range"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"i", "x"}
    assert analyzer.names.unclassified_deep == {"range"}


def sample_bad_list_comprecension(x):
    n = i
    return [i+n for i in range(x)]

def test_bad_list_comprencension():
    with pytest.raises(Exception):
        sample_bad_list_comprecension(3)
    analyzer = analyze_names_in_function(sample_bad_list_comprecension)["analyzer"]
    assert analyzer.imported_packages_deep == set()
    assert analyzer.names.accessible == {"i", "x", "range", "n"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"x", "n"}
    assert analyzer.names.unclassified_deep == {"range","i"}

def sample_for_loop(x):
    total = 0
    for i in range(x):
        total += i
    for i,y in enumerate(range(x)):
        total += i+ y
    return total

def test_for_loop():
    sample_for_loop(3)
    dependencies = analyze_names_in_function(sample_for_loop)
    analyzer = dependencies["analyzer"]
    assert analyzer.imported_packages_deep == set()
    assert analyzer.names.accessible == {"total","i", "x", "y", "range", "enumerate"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"x", "i", "y", "total"}
    assert analyzer.names.unclassified_deep == {"range", "enumerate"}

def simple_nested(x):
    def nested(y):
        import math
        return math.sqrt(y)
    return nested(x)

def test_simple_nested():
    assert simple_nested(4) == 2
    analyzer = analyze_names_in_function(simple_nested)["analyzer"]
    assert analyzer.imported_packages_deep == {"math"}
    assert analyzer.names.accessible == {"nested", "x"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"nested", "x"}
    assert analyzer.names.unclassified_deep == set()

def bad_simple_nested(x):
    del sys
    sys.api_version
    def nested(y):
        return math.sqrt(y)
    return nested(x)

def test_bad_simple_nested():
    with pytest.raises(Exception):
        bad_simple_nested(4)
    analyzer = analyze_names_in_function(bad_simple_nested)["analyzer"]
    assert analyzer.imported_packages_deep == set()
    assert analyzer.names.accessible == {"nested", "x", "sys"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"nested", "x"}
    assert analyzer.names.unclassified_deep == {"math","sys"}


def simple_nested_2(x):
    import math
    def nested(y):
        return math.sqrt(float(y))
    return nested(x)

def test_simple_nested_2():
    assert simple_nested_2(4) == 2
    analyzer = analyze_names_in_function(simple_nested_2)["analyzer"]
    assert analyzer.imported_packages_deep == {"math"}
    assert analyzer.names.accessible == {"nested", "x", "math"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"math"}
    assert analyzer.names.local == {"nested", "x"}
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
    analyzer = analyze_names_in_function(simple_nonlocal)["analyzer"]
    assert analyzer.imported_packages_deep == {"math"}
    assert analyzer.names.accessible == {"nested", "x", "z", "mmm"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"mmm"}
    assert analyzer.names.local == {"nested", "x", "z"}
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
    analyzer = analyze_names_in_function(simple_global)["analyzer"]
    assert analyzer.imported_packages_deep == {"math"}
    assert analyzer.names.accessible == {"nested", "x", "m"}
    assert analyzer.names.explicitly_global_unbound_deep == {"float"}
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"m"}
    assert analyzer.names.local == {"nested", "x"}
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
    analyzer = analyze_names_in_function(simple_deep)
    tree = analyzer["tree"]
    analyzer = analyzer["analyzer"]
    assert analyzer.imported_packages_deep == {"math","ast", "pandas"}
    assert analyzer.names.accessible == {"nested","second_nested", "x", "m"}
    assert analyzer.names.explicitly_global_unbound_deep == {"float","print"}
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"m"}
    assert analyzer.names.local == {"nested","second_nested", "x"}
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
    analyzer = analyze_names_in_function(simple_deep)
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
    analyzer = analyze_names_in_function(simple_yeld)
    tree = analyzer["tree"]
    analyzer = analyzer["analyzer"]
    assert analyzer.n_yelds == 2

def simple_exceptioms():
    try:
        pass
    except Exception as e:
        print(e)
    finally:
        a = 5

def test_simple_exceptioms():
    simple_exceptioms()
    analyzer = analyze_names_in_function(simple_exceptioms)
    tree = analyzer["tree"]
    analyzer = analyzer["analyzer"]
    assert analyzer.imported_packages_deep == set()
    assert analyzer.names.accessible == {"print", "Exception", "e", "a"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == set()
    assert analyzer.names.local == {"e", "a"}
    assert analyzer.names.unclassified_deep == {"Exception", "print"}

def simple_with():
    import contextlib
    with contextlib.suppress(Exception) as suppressed:
        pass

def test_simple_with():
    simple_with()
    analyzer = analyze_names_in_function(simple_with)
    tree = analyzer["tree"]
    analyzer = analyzer["analyzer"]
    assert analyzer.imported_packages_deep == {"contextlib"}
    assert analyzer.names.accessible == {"contextlib", "Exception", "suppressed"}
    assert analyzer.names.explicitly_global_unbound_deep == set()
    assert analyzer.names.explicitly_nonlocal_unbound_deep == set()
    assert analyzer.names.imported == {"contextlib"}
    assert analyzer.names.local == {"suppressed"}
    assert analyzer.names.unclassified_deep == {"Exception"}