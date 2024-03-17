from pythagoras._05_events_and_exceptions.type_retrievers import (
    retrieve_IdempotentFn_class
    , retrieve_AutonomousFn_class
    , retrieve_IdempotentFnExecutionResultAddr_class
    , retrieve_IdempotentFnExecutionContext_class)


import pythagoras as pth

def test_type_retrievers():
    assert retrieve_IdempotentFn_class() == pth.IdempotentFn
    assert retrieve_AutonomousFn_class() == pth.AutonomousFn
    assert retrieve_IdempotentFnExecutionResultAddr_class(
        ) == pth.IdempotentFnExecutionResultAddr
    assert retrieve_IdempotentFnExecutionContext_class(
        ) == pth.IdempotentFnExecutionContext
