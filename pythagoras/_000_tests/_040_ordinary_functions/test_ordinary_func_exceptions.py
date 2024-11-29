from pythagoras import OrdinaryFn, DataPortal, _PortalTester, OrdinaryCodePortal
import time


def simple_function_exception(a:int,b:int) -> int:
    return (a+b)/0





def test_ordinary_function_excptn(tmpdir):
    # tmpdir = 3*"ORDINARY_FN_EXCPTN_"+str(int(time.time()))
    try:
        with _PortalTester(OrdinaryCodePortal, tmpdir) as p:
            crash_history = p.portal.crash_history
            assert len(p.portal.crash_history) == 0
            f = OrdinaryFn(simple_function_exception)
            result = f(a=1,b=2)
            print(result)
    except:
        pass
    assert len(crash_history) == 2



def fibonacci_with_exception(n:int) -> int:
    if n < 2:
        return n/0
    return fibonacci_with_exception(n=n-1) + fibonacci_with_exception(n=n-2)

def test_ordinary_function_with_recursion(tmpdir):
    # tmpdir = 3 * "ORDINARY_FN_WITH_RECURSION_" + str(int(time.time()))
    try:
        with _PortalTester(DataPortal, tmpdir) as p:
            crash_history = p.portal.crash_history
            assert len(p.portal.crash_history) == 0
            f = OrdinaryFn(fibonacci_with_exception)
            result = f(n=4)
    except:
        pass
    assert len(crash_history) == 2




