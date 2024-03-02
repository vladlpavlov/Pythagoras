from typing import Any

from pythagoras._99_misc_utils.find_in_callstack import find_in_callstack

def isinstance_txt(obj:Any, type_name:str)->bool:
    """Check if an object is an instance of a type specified by a string name.

    This function extends the functionality of the built-in isinstance function
    by allowing the type to be specified as a string.

    It first attempts to evaluate the string to a type using the eval function.
    If this raises a exception (indicating that the type is not directly
    accessible in the current scope), it then searches the call stack
    for an object that matches the type name. If a single matching type
    is found in the stack, it checks if `obj` is an instance of this type.

    Parameters:
    obj (Any): The object to be checked.
    type_name (str): The name of the type as a string.

    Returns:
    bool: True if `obj` is an instance of the type specified by `type_name`,
    False otherwise
    """

    assert isinstance(type_name, str)
    try:
        if isinstance(obj, eval(type_name)):
            return True
    except NameError:
        candidates = find_in_callstack(type_name)
        assert len(candidates) == 1
        return isinstance(obj, candidates[0])
    return False