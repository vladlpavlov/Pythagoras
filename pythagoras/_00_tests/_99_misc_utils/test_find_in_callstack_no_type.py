from pythagoras._05_events_and_exceptions.find_in_callstack import find_in_callstack

# Test variables
global_var = "global_value"
test_var = "test"

def test_find_in_callstack_basic():
    # Test for finding a global variable
    assert len(find_in_callstack("test_var")) == 1

def function_with_var():
    test_var = "local test"
    return find_in_callstack("test_var")

#
# def function_without_var():
#     return find_in_stack("test_var")

def nested_function_level_1():
    local_var_level_1 = "level_1"
    return nested_function_level_2()

def nested_function_level_2():
    local_var_level_2 = "level_2"
    return find_in_callstack("nested_var")

def test_find_in_callstack_no_object():
    # Test for no object found
    assert not find_in_callstack("non_existent_var")

def test_find_in_callstack_multiple_objects():
    # Test for multiple objects with the same name
    objects = function_with_var()
    assert len(objects) == 2
    assert "local test" in objects
    assert "test" in objects


def test_find_global_object():
    # Test for finding a global variable
    assert global_var in find_in_callstack("global_var")

def test_find_in_callstack_multi_level_nesting():
    # Test for multi-level nested function calls
    nested_var = "nested_value"
    objects = nested_function_level_1()
    assert nested_var in objects
    assert "level_1" not in objects
    assert "level_2" not in objects

def recursive_function(counter):
    if counter > 0:
        return recursive_function(counter - 1)
    return find_in_callstack("recursive_var")

def test_find_in_callstack_recursion():
    recursive_var = "recursive"
    objects = recursive_function(5)
    assert recursive_var in objects

def advanced_recursive_function(counter):
    advanced_recursive_var = [i for i in range(counter)]
    if counter > 0:
        return advanced_recursive_function(counter - 1)
    return find_in_callstack("advanced_recursive_var")

def test_find_in_callstack_advanced_recursion():
    advanced_recursive_var = "advanced_recursive"
    objects = advanced_recursive_function(5)
    assert len(objects) == 7

def test_import():
    r = find_in_callstack("pytest")
    assert len(r) == 1