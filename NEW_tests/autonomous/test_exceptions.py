from pythagoras._autonomous import *

def test_exceptions():
    assert issubclass(FunctionAutonomicityError, Exception)