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


def retrieve_FunctionExecutionResultAddress_class() -> type:
    """Return the FunctionExecutionResultAddress class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].FunctionExecutionResultAddress


def retrieve_FunctionExecutionContext_class() -> type:
    """Return the FunctionExecutionContext class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].FunctionExecutionContext



