def is_reserved_identifier(id: str) -> bool:
    """Checks if the given id is reserved by Pyhtagoras.

    An id is reserved if it starts with "__pth_".

    Reserved ids cannot be used as names for autonomous and idempotent
    functions. They also can not be used as names for function arguments of the
    autonomous and idempotent functions. Finally, autonomous and idempotent
    functions ar enot allowed to access an attribute of any object,
    if the attribute's name is a reserved id

    :param id: The id to check.
    :return: True if the id is reserved, False otherwise.
    """
    return id.startswith("__pth_")