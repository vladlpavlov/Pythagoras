def is_reserved_identifier(id: str) -> bool:
    """Checks if the given id is reserved by Pyhtagoras.

    An id is reserved if it starts with "__pth_". If id is reserved, Pythagoras
    may assign some special meaning to it. You should never explicitly use
    reserved ids in your code if your code uses Pythagoras

    :param id: The id to check.
    :return: True if the id is reserved, False otherwise.
    """

    return id.startswith("_pth_")
