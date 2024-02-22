import inspect
from typing import List, Any

def find_in_stack(obj_name: str) -> List[Any]:
    """ Search the entire call stack for an object with the specified name.

    This function iterates through the current call stack
    using the `inspect` module. It checks both the local and global
    namespace of each frame for the specified object name.
    If an object with the given name is found, it's added to the list
    of found objects. To avoid duplicates (in case the same object appears
    in multiple frames), the function uses the `id` of the object
    as a key in a dictionary, effectively filtering out duplicates.

    Parameters:
    obj_name (str): The name of the object to search for in the stack.

    Returns:
    List[Any]: A list of objects found in the stack with the specified name.
    The list contains no duplicates.
    """
    found_objects = []

    for frame_info in inspect.stack():
        frame = frame_info.frame
        if obj_name in frame.f_locals:
            found_objects.append(frame.f_locals[obj_name])
        if obj_name in frame.f_globals:
            found_objects.append(frame.f_globals[obj_name])

    flipper = dict()
    for obj in found_objects:
        flipper[id(obj)] = obj

    found_objects = list(flipper.values())

    return found_objects

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
        candidates = find_in_stack(type_name)
        assert len(candidates) == 1
        return isinstance(obj, candidates[0])
    return False