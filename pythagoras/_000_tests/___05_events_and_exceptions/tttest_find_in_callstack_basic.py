from pythagoras.___OLD_05_events_and_exceptions.find_in_callstack import (
    find_local_var_in_callstack)


def test_unexisting():
    assert find_local_var_in_callstack("_____unexisting__") == []


def test_simple_local():
    a = 10
    assert find_local_var_in_callstack("a") == [10]


b = 20
def test_simple_global():
    b = 30
    assert find_local_var_in_callstack("b") == [30]

def test_typed_global():
    b = "forty"
    assert find_local_var_in_callstack("b", int) == []
    assert find_local_var_in_callstack("b", str) == ["forty"]
    assert find_local_var_in_callstack("b", "int") == []
    assert find_local_var_in_callstack("b", "str") == ["forty"]


x = 1.23456789
def test_nested():
    x = 12.3456789
    def inner():
        x = 123.456789
        assert find_local_var_in_callstack("x") == [123.456789, 12.3456789]

    inner()


var = "Global Hello"
def test_nested_typed():
    var = "Hello"
    def inner():
        var = {}
        assert find_local_var_in_callstack("var") == [{}, "Hello"]
        assert find_local_var_in_callstack("var", str) == ["Hello"]
        assert find_local_var_in_callstack("var", dict) == [{}]
        assert find_local_var_in_callstack("var", "str") == ["Hello"]
        assert find_local_var_in_callstack("var", "dict") == [{}]

    inner()


class A:
    pass

def test_nested_custom_class():
    var = A()
    def inner():
        var = A()
        assert len(find_local_var_in_callstack("var")) == 2

    inner()

def recursive_function(counter):
    if counter > 0:
        return recursive_function(counter - 1)
    return find_local_var_in_callstack("recursive_var")

def test_find_in_callstack_recursion():
    recursive_var = "recursive"
    objects = recursive_function(5)
    assert recursive_var in objects

def advanced_recursive_function(counter):
    advanced_recursive_var = [i for i in range(counter)]
    if counter > 0:
        return advanced_recursive_function(counter - 1)
    return find_local_var_in_callstack("advanced_recursive_var")

def test_find_in_callstack_advanced_recursion():
    advanced_recursive_var = "advanced_recursive"
    objects = advanced_recursive_function(5)
    assert len(objects) == 7