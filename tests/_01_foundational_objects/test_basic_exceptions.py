from pythagoras._01_foundational_objects.basic_exceptions import *

def test_exceptions():
    assert issubclass(PythagorasException, Exception)