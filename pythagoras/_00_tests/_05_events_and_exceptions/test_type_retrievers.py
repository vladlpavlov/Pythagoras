from pythagoras._05_events_and_exceptions.type_retrievers import (
    retrieve_IdempotentFunction_class
    ,retrieve_AutonomousFunction_class
    ,retrieve_FuncOutputAddress_class)

import pythagoras as pth

def test_type_retrievers():
    assert retrieve_IdempotentFunction_class(None) == pth.IdempotentFunction
    assert retrieve_AutonomousFunction_class(None) == pth.AutonomousFunction
    assert retrieve_FuncOutputAddress_class(None) == pth.FuncOutputAddress

