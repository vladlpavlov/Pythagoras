import inspect
from functools import cache

import autopep8

from pythagoras.NEW_utils import get_normalized_function_source

def f_docstring():
    """ This is a CRAZY docstring"""
    return 123456

def f_comments():
    def internal(a:int):
        b=24
        # This is a STRANGE comment
        return a+b
    return internal(58)

@cache
def f_with_decorator(*args,**kwargs):
    return len(args)+len(kwargs)

def test_basics():
    no_docsting = get_normalized_function_source(f_docstring)
    assert "CRAZY" in inspect.getsource(f_docstring)
    assert "CRAZY" not in no_docsting
    assert no_docsting != autopep8.fix_code(inspect.getsource(f_docstring))
    assert no_docsting == autopep8.fix_code(no_docsting)

    no_comments = get_normalized_function_source(f_comments)
    assert "STRANGE" in inspect.getsource(f_comments)
    assert "STRANGE" not in no_comments
    assert no_comments != autopep8.fix_code(inspect.getsource(f_comments))
    assert no_comments == autopep8.fix_code(no_comments)

    no_decorator = get_normalized_function_source(f_with_decorator)
    assert "cache" in inspect.getsource(f_with_decorator)
    assert "cache" not in no_decorator

def a2(x): # a sample function to test
    print(10 # why i sit here?
        ,20)
    return x*x

def test_inclosed():
    global a2
    old_a2 = get_normalized_function_source(a2)
    del a2

    @cache
    def a2(x):

        print (10, 20)
        # unneeded comment
        return (x * x)

    new_a2 = get_normalized_function_source(a2)
    assert old_a2 == new_a2
    assert new_a2 == autopep8.fix_code(new_a2)