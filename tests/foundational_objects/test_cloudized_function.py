import pytest
from persidict import FileDirDict

import pythagoras as pth
from pythagoras.foundational_objects.cloud_funcs_addresses import CloudizedFunction
from pythagoras.misc_utils.global_state_management import (
    initialize, _clean_global_state)

def simple_func_0():
    return 5

def simple_func_1(a):
    return a

def simple_func_2(a,b):
    return a+b


def test_cloudfunc_simple(tmpdir):

    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")
    island = pth.get_island("test")

    assert simple_func_0.__name__ not in island
    cloud_func_0 = CloudizedFunction(simple_func_0)
    assert cloud_func_0._naked_call() == 5
    assert simple_func_0.__name__ in island

    assert simple_func_1.__name__ not in island
    cloud_func_1 = CloudizedFunction(simple_func_1)
    assert cloud_func_1._naked_call(a=10) == 10
    assert simple_func_1.__name__ in island

    assert simple_func_2.__name__ not in island
    cloud_func_2 = CloudizedFunction(simple_func_2)
    assert cloud_func_2._naked_call(a=4,b=6) == 10
    len_1 = len(pth.value_store)
    assert cloud_func_2._naked_call(b=6, a=4) == 10
    len_2 = len(pth.value_store)
    assert len_1 == len_2
    assert simple_func_2.__name__ in island

def inner_func():
    return 1234567890

def outer_func():
    result = inner_func()
    return result

def test_simple_cloudfunc_chain(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")
    island = pth.get_island("test")

    inner_cloud_func = CloudizedFunction(inner_func)
    outer_cloud_func = CloudizedFunction(outer_func)
    assert outer_cloud_func._naked_call() == 1234567890

def test_cloufunc_serrialization(tmpdir):
    file_dict = FileDirDict(tmpdir)

    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")
    inner_cloud_func = CloudizedFunction(inner_func)
    outer_cloud_func = CloudizedFunction(outer_func)
    file_dict["tmp","outer_cloud_func"] = outer_cloud_func

    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")
    outer_cloud_func_2 = file_dict["tmp","outer_cloud_func"]
    assert outer_cloud_func_2._naked_call() == 1234567890

    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")
    outer_cloud_func = CloudizedFunction(outer_func)
    with pytest.raises(Exception):
        file_dict["tmp","outer_cloud_func"] = outer_cloud_func


def aa(x):
    if x <= 0:
        return 0
    else:
        return 1+bb(x-1)

def bb(x):
    if x <= 0:
        return 0
    else:
        return 1+aa(x-1)

def test_2_cloudfuncs_recursion(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")

    aa_cloud_func = CloudizedFunction(aa)
    bb_cloud_func = CloudizedFunction(bb)

    assert aa_cloud_func._naked_call(x=10) == 10
    assert bb_cloud_func._naked_call(x=10) == 10

def test_failed_2_cloudfuncs_recursion(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")

    aa_cloud_func = CloudizedFunction(aa)

    with pytest.raises(Exception):
        aa_cloud_func._naked_call(x=10)


def aaa(x):
    if x <= 0:
        return 0
    else:
        return 1+bbb(x-1)

def bbb(x):
    if x <= 0:
        return 0
    else:
        return 1+ccc(x-1)

def ccc(x):
    if x <= 0:
        return 0
    else:
        return 1+aaa(x-1)

def test_3_cloudfuncs_recursion(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")

    aaa_cloud_func = CloudizedFunction(aaa)
    bbb_cloud_func = CloudizedFunction(bbb)
    ccc_cloud_func = CloudizedFunction(ccc)

    assert aaa_cloud_func._naked_call(x=100) == 100
    assert bbb_cloud_func._naked_call(x=200) == 200
    assert ccc_cloud_func._naked_call(x=300) == 300

def test_failed_3_cloudfuncs_recursion(tmpdir):
    _clean_global_state()
    initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")

    aaa_cloud_func = CloudizedFunction(aaa)
    bbb_cloud_func = CloudizedFunction(bbb)

    with pytest.raises(Exception):
        aaa_cloud_func._naked_call(x=100)
    with pytest.raises(Exception):
        bbb_cloud_func._naked_call(x=200)




