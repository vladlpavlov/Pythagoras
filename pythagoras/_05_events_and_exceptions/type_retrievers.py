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


def retrieve_IdempotentFunctionExecutionResultAddress_class() -> type:
    """Return the IdempotentFunctionExecutionResultAddress class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].IdempotentFunctionExecutionResultAddress


def retrieve_IdempotentFunctionExecutionContext_class() -> type:
    """Return the IdempotentFunctionExecutionContext class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].IdempotentFunctionExecutionContext



