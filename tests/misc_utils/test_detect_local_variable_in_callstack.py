import pytest
from pythagoras.misc_utils.events_and_exceptions import detect_local_variable_in_callstack

class TestClass:
    def __init__(self,a):
        self.a = a

def outer_function_for_test():
    test_variable = TestClass(5)

    def middle_function():
        def inner_function():
            return detect_local_variable_in_callstack('test_variable', TestClass)

        return inner_function()

    return middle_function()

def test_detect_existing_local_variable_nested_call():
    assert outer_function_for_test() is not None
    assert isinstance(outer_function_for_test(), TestClass)
    assert outer_function_for_test().a == 5

def test_detect_non_existing_variable_name_nested_call():
    def outer_function():
        non_existing_variable = TestClass(42)

        def middle_function():
            def inner_function():
                return detect_local_variable_in_callstack('some_other_name', TestClass)

            return inner_function()

        return middle_function()
    result = outer_function()
    assert result is None

def test_detect_existing_variable_different_type_nested_call():
    def outer_function():
        test_variable = 123  # Integer, not TestClass

        def middle_function():
            def inner_function():
                return detect_local_variable_in_callstack('test_variable', TestClass)

            return inner_function()

        return middle_function()

    assert outer_function() is None

def test_detect_invalid_input_types_nested_call():
    def outer_function():
        test_variable = TestClass(2024)

        def middle_function():
            def inner_function():
                with pytest.raises(AssertionError):
                    detect_local_variable_in_callstack(123, TestClass)
                with pytest.raises(AssertionError):
                    detect_local_variable_in_callstack('test_variable', 'TestClass')

            return inner_function()

        return middle_function()

    outer_function()

def test_detect_empty_variable_name_nested_call():
    def outer_function():
        test_variable = TestClass(-1)

        def middle_function():
            def inner_function():
                with pytest.raises(AssertionError):
                    detect_local_variable_in_callstack('', TestClass)

            return inner_function()

        return middle_function()

    outer_function()
