import pythagoras as pth
from pythagoras import ordinary
@pth.ordinary()
def simple_function_1(a:int,b:int)->int:
    return a+b

@ordinary()
def simple_function_2(a:int,b:int)->int:
    return a*b

def test_simple():
    assert simple_function_1(a=1,b=2)==3
    assert simple_function_2(a=2,b=3)==6
    assert simple_function_1.decorator=="@pth.ordinary()"



