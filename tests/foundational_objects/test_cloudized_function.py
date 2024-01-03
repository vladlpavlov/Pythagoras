import pythagoras as pth
from pythagoras.foundational_objects.base_classes_for_addresses_and_functions import CloudizedFunction
from pythagoras.utils.global_state_initializer import (
    initialize, _clean_global_state)

def simple_func_0():
    return 5

def simple_func_1(a):
    return a

def simple_func_2(a,b):
    return a+b

def test_cloudfunc_simple(tmpdir):

    _clean_global_state()
    initialize(base_dir=tmpdir, island_name="test", cloud_type="local")

    cloud_func_0 = CloudizedFunction(simple_func_0)
    assert cloud_func_0._inprocess() == 5

    cloud_func_1 = CloudizedFunction(simple_func_1)
    assert cloud_func_1._inprocess(a=10) == 10

    cloud_func_2 = CloudizedFunction(simple_func_2)
    assert cloud_func_2._inprocess(a=4,b=6) == 10
    len_1 = len(pth.value_store)
    assert cloud_func_2._inprocess(b=6, a=4) == 10
    len_2 = len(pth.value_store)
    assert len_1 == len_2

