from copy import copy

import pytest
from pythagoras._05_events_and_exceptions.find_in_callstack import find_in_callstack

class TestClass:
    def __init__(self,a):
        self.a = a


def test_detect_existing_variable_name_nested_call():
    def outer_function():
        my_var = TestClass(42)

        def middle_function():
            def inner_function():
                return find_in_callstack('my_var', TestClass)

            return inner_function()

        return middle_function()

    result = outer_function()
    assert len(result) == 1

def test_detect_2_existing_variable_names_nested_call():
    def outer_function():
        my_var = TestClass(42)

        def middle_function():
            my_var = TestClass(24)
            def inner_function():
                return find_in_callstack('my_var', TestClass)

            return inner_function()

        return middle_function()

    result = outer_function()
    assert len(result) == 2
    assert result[0].a == 24
    assert result[1].a == 42

def test_detect_2_existing_variables_different_types():
    def outer_function():
        my_var = TestClass(42)

        def middle_function():
            my_var = 24.0
            def inner_function():
                return find_in_callstack('my_var', TestClass)

            return inner_function()

        return middle_function()

    result = outer_function()
    assert len(result) == 1

def test_dedup():
    def outer_function():
        my_var = TestClass(42)
        def middle_function(v):
            my_var = v
            def inner_function():
                return find_in_callstack('my_var', TestClass)

            return inner_function()

        return middle_function(my_var)

    result = outer_function()
    assert len(result) == 1

def test_no_dedup():
    def outer_function():
        my_var = TestClass(42)
        def middle_function(v):
            my_var = v
            def inner_function():
                return find_in_callstack('my_var', TestClass)

            return inner_function()

        return middle_function(copy(my_var))

    result = outer_function()
    assert len(result) == 2


def test_detect_non_existing_variable_name_nested_call():
    def outer_function():
        non_existing_variable = TestClass(42)

        def middle_function():
            def inner_function():
                return find_in_callstack('some_other_name', TestClass)

            return inner_function()

        return middle_function()
    result = outer_function()
    assert len(result) == 0

def test_detect_existing_variable_different_types_nested_call():
    def outer_function():
        test_variable = 123  # Integer, not TestClass

        def middle_function():
            def inner_function():
                return find_in_callstack('test_variable', TestClass)

            return inner_function()

        return middle_function()

    result = outer_function()
    assert len(result) == 0

def test_detect_invalid_input_types_nested_call():
    def outer_function():
        test_variable = TestClass(2024)

        def middle_function():
            def inner_function():
                with pytest.raises(AssertionError):
                    find_in_callstack(123, TestClass)
                with pytest.raises(AssertionError):
                    find_in_callstack('test_variable', 'TestClass')

            return inner_function()

        return middle_function()

    outer_function()

def test_detect_empty_variable_name_nested_call():
    def outer_function():
        test_variable = TestClass(-1)

        def middle_function():
            def inner_function():
                with pytest.raises(AssertionError):
                    find_in_callstack('', TestClass)

            return inner_function()

        return middle_function()

    outer_function()