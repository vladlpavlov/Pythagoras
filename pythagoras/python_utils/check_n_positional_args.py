from typing import Callable
import inspect

def accepts_unlimited_positional_args(func: Callable) -> bool:
    """Check if a function accepts an arbitrary number of positional arguments.

    This function inspects the signature of the provided callable and
    checks if it includes a parameter defined with `*args`,
    which allows it to accept any number of positional arguments.

    Parameters:
    func (Callable): The function or callable object whose signature is
    to be inspected.

    Returns:
    bool: True if `func` accepts an arbitrary number of positional arguments
    (`*args`), False otherwise.
    """

    signature = inspect.signature(func)
    for param in signature.parameters.values():
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            return True
    return False

