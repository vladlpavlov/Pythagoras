from pythagoras._02_ordinary_functions.ordinary_funcs import OrdinaryFunction


def simple_fucntion(a:int,b:int) -> int:
    return a+b
def test_ordinary_function():
    f = OrdinaryFunction(simple_fucntion)
    result = f(a=1,b=2)
    assert result == 3

def fibonacci(n:int) -> int:
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def test_ordinary_function_with_recursion():
    f = OrdinaryFunction(fibonacci)
    result = f(n=6)
    assert result == 8
