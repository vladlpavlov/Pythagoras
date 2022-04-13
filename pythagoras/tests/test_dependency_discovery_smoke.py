from pythagoras._dependency_discovery import _all_dependencies_one_func
from typing import Any

def f():
    return 1

def kuku():
    return 2

def rep_f():
    return f()

def both():
    return f()+kuku()

def a():
    return both()

def b():
    return a()

def o():
    return 589

def e():
    return True

def long_function(n:int) -> Any:
    result = f()
    result += kuku()
    result += both()
    result += o()
    if e():
        return result
    else:
        return -100

def turn_left():
    turn_right()

def turn_right():
    turn_left()

def test_dependency_discovery():
    functions_dict = {}
    for fn in [f, kuku, a, rep_f, long_function, both, b, o, e, turn_left, turn_right]:
        functions_dict[fn.__name__] = fn
    assert len(_all_dependencies_one_func("f", functions_dict)) == 1
    assert len(_all_dependencies_one_func("kuku", functions_dict)) == 1
    assert len(_all_dependencies_one_func("o", functions_dict)) == 1
    assert len(_all_dependencies_one_func("e", functions_dict)) == 1
    assert len(_all_dependencies_one_func("rep_f", functions_dict)) == 2
    assert len(_all_dependencies_one_func("both", functions_dict)) == 3
    assert len(_all_dependencies_one_func("a", functions_dict)) == 4
    assert len(_all_dependencies_one_func("b", functions_dict)) == 5
    assert len(_all_dependencies_one_func("long_function", functions_dict)) == 6
    assert len(_all_dependencies_one_func("turn_left",functions_dict)) == 2