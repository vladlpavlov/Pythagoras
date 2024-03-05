import sys

def retrieve_IdempotentFunction_class() -> type:
    """Return the IdempotentFunction class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].IdempotentFunction


def retrieve_AutonomousFunction_class() -> type:
    """Return the AutonomousFunction class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].AutonomousFunction


def retrieve_FuncOutputAddress_class() -> type:
    """Return the FuncOutputAddress class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].FuncOutputAddress



