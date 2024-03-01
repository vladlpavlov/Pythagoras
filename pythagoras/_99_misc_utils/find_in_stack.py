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
