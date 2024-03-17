import sys

def retrieve_IdempotentFn_class() -> type:
    """Return the IdempotentFn class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].IdempotentFn


def retrieve_AutonomousFn_class() -> type:
    """Return the AutonomousFn class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].AutonomousFn


def retrieve_IdempotentFnExecutionResultAddr_class() -> type:
    """Return the IdempotentFnExecutionResultAddr class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].IdempotentFnExecutionResultAddr


def retrieve_IdempotentFnExecutionContext_class() -> type:
    """Return the IdempotentFnExecutionContext class.

    This is for-internal-use-only function, created to
    avoid circular import dependencies.
    """
    return sys.modules['pythagoras'].IdempotentFnExecutionContext



