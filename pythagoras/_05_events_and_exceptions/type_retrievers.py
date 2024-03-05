import sys

def retrieve_IdempotentFunction_class(obj):
    """Return the IdempotentFunction class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].IdempotentFunction


def retrieve_AutonomousFunction_class(obj):
    """Return the AutonomousFunction class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].AutonomousFunction


def retrieve_FuncOutputAddress_class(obj):
    """Return the FuncOutputAddress class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].FuncOutputAddress



