import pytest
from pythagoras._040_ordinary_functions.assert_ordinarity import assert_ordinarity



def test_lambdas():
    with pytest.raises(AssertionError):
        assert_ordinarity(lambda x: x**2)


class DemoClass:
    def regular_method(self):
        pass

    @classmethod
    def class_method(cls):
        pass

    @staticmethod
    def static_method():
        pass

def test_methods():
    demo_obj = DemoClass()
    with pytest.raises(AssertionError):
        assert_ordinarity(demo_obj.regular_method)
    with pytest.raises(AssertionError):
        assert_ordinarity(demo_obj.class_method)

    # TODO: decide how to handle static methods
    # currently they are treated as ordinary functions
    # with pytest.raises(AssertionError):
    #     assert_ordinarity(demo_obj.static_method)

def outer_function():
    return 0

def test_ordinary_functions():
    def inner_function():
        return 1

    assert_ordinarity(outer_function)
    assert_ordinarity(inner_function)

def test_closure():
    i = 5
    def inner_function():
        return i

    with pytest.raises(AssertionError):
        assert_ordinarity(inner_function)

def test_builtin_functions():
    with pytest.raises(AssertionError):
        assert_ordinarity(print)
    with pytest.raises(AssertionError):
        assert_ordinarity(len)

def test_async_functions():
    async def async_function():
        pass

    with pytest.raises(AssertionError):
        assert_ordinarity(async_function)
