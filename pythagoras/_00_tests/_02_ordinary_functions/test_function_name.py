from pythagoras._02_ordinary_functions.function_name import (
    get_function_name_from_source)

from inspect import getsource

def test_get_function_name_from_source():
    def a_function():
        pass

    name = get_function_name_from_source(getsource(a_function))
    assert name == "a_function"

    def another_function():
        pass

    name = get_function_name_from_source(getsource(another_function))
    assert name == "another_function"

def test_get_function_name_from_source_with_decorators():
    def sample_decorator(f):
        return f

    @sample_decorator
    def sample_function():
        pass

    name = get_function_name_from_source(getsource(sample_function))
    assert name == "sample_function"
