import inspect
from typing import List, Any

def find_in_callstack(
        name_to_find: str
        , class_to_find: None | type = None
        ) -> List[Any]:
    """ Search the entire call stack for objects with the specified name/type.

    If the callstack contains objects
    with name name_to_find and type class_to_find,
    the function will return these objects as a list,
    starting with the innermost object.

    If class_to_find is None, the function will
    look for objects with any type.

    Duplicate objects are removed from the resulting list.

    Parameters:
    name_to_find (str): The name of the object to search for.
    class_to_find (None | type): The type of the object to search for.

    Returns:
    List[Any]: A list of objects found in the stack
    with the specified name/type.
    The list contains no duplicates.
    """

    assert isinstance(name_to_find, str) and len(name_to_find)
    assert class_to_find is None or inspect.isclass(class_to_find)

    found_objects = []

    for frame_info in inspect.stack():
        frame = frame_info.frame
        if name_to_find in frame.f_locals:
            candidate = frame.f_locals[name_to_find]
            if class_to_find is None or isinstance(candidate, class_to_find):
                found_objects.append(candidate)
        if name_to_find in frame.f_globals:
            candidate = frame.f_globals[name_to_find]
            if class_to_find is None or isinstance(candidate, class_to_find):
                found_objects.append(candidate)

    dedup_dict = dict()
    for obj in found_objects:
        dedup_dict[id(obj)] = obj

    found_objects = list(dedup_dict.values())

    return found_objects