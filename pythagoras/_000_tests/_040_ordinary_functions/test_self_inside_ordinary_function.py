import pythagoras as pth
from pythagoras import ordinary

@ordinary()
def simple_o_function(a:int,b:int)->int:
    assert isinstance(self,pth.OrdinaryFn)
    return a+b

def test_simple():
    assert simple_o_function(a=11,b=1100)==1111