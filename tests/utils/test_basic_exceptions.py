from pythagoras.utils.basic_exceptions import *

def test_exceptions():
    assert issubclass(PythagorasException, Exception)