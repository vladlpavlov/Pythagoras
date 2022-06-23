import ast
import gc
from functools import cache
from pprint import pprint

from pythagoras import *
import pytest
from moto import mock_s3


def fff():
    return int(1)

def ggg(a:int):
    return int(a*a)

def test_SharedStorage_P2P_Cloud_func1args(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir, p_purity_checks=0.5)

    global fff
    fff = my_cloud.publish(fff)

    assert len(my_cloud.original_functions) == len(my_cloud.cloudized_functions) == 1

    for i in range(4): assert fff() == 1
    assert len(my_cloud.value_store) == 4
    assert len(my_cloud.func_output_store)  == 1

    global ggg
    ggg = my_cloud.publish(ggg)

    print(f'{("ggg" in locals())=}')

    assert len(my_cloud.original_functions) == 2
    assert len(my_cloud.cloudized_functions) == 2

    for i in range(4): assert ggg(a=1) == 1

    assert len(my_cloud.value_store) == 7
    assert len(my_cloud.func_output_store) == 2

    for i in range(4): assert ggg(a=2) == 4

    assert len(my_cloud.value_store) == 11
    assert len(my_cloud.func_output_store) == 3

    for i in range(4):  assert ggg(a=3) == 9

    assert len(my_cloud.value_store) == 15
    assert len(my_cloud.func_output_store) == 4

    for i in range(4):
        assert ggg.sync_parallel(kw_args(a=i) for i in range(10)) == (
            [i*i for i in range(10)])

    addr = my_cloud.sync_local_inprocess_function_call("ggg", kw_args(a=100))
    value_store_len = len(my_cloud.value_store)

    del ggg, fff, my_cloud

    P_Cloud_Implementation._reset()


    my_new_cloud = SharedStorage_P2P_Cloud(
        base_dir=tmpdir
        , p_purity_checks=0.5
        , restore_from = addr)

    assert ggg(a=100) == 10000

    for i in range(4):
        assert ggg.sync_parallel(kw_args(a=i) for i in range(10)) == (
            [i*i for i in range(10)])

    assert len(my_new_cloud.value_store) == value_store_len

    P_Cloud_Implementation._reset()



def hihihi(*, x: int, y: int):
    return x + 100 * y

def test_SharedStorage_P2P_Cloud_func2args(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir, p_purity_checks=0.5)

    global hihihi
    hihihi = my_cloud.publish(hihihi)

    assert hihihi(x=1, y=2) == hihihi(x=1, y=2) == hihihi(y=2, x=1)


    assert len(my_cloud.value_store) == 6
    assert len(my_cloud.func_output_store) == 1

    assert hihihi.ready(x=1, y=2)
    assert not hihihi.ready(x=-1, y=-2)

    assert len(my_cloud.value_store) == 10

    P_Cloud_Implementation._reset()



def lyslyslya(*, x: float, y: float, z:float):
    return x + 100 * y + z*10_000

def test_SharedStorage_P2P_Cloud_func3args(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir, p_purity_checks=0.5)

    global lyslyslya
    lyslyslya = my_cloud.publish(lyslyslya)


    assert lyslyslya(x=1, y=2, z=3) == lyslyslya(z=3, x=1, y=2)
    assert lyslyslya(x=1, y=2, z=3) == lyslyslya(z=3, y=2, x=1)
    assert lyslyslya(y=2, x=1, z=3) == lyslyslya(z=3, y=2, x=1)

    assert len(my_cloud.value_store) == 7
    assert len(my_cloud.func_output_store) == 1

    assert lyslyslya.ready(y=2, x=1, z=3)
    assert not lyslyslya.ready(y=2000, x=1, z=3)

    P_Cloud_Implementation._reset()


def test_multiple_clouds(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(
        base_dir=str(tmpdir), p_purity_checks=0.5)
    second_cloud = SharedStorage_P2P_Cloud(
        base_dir=str(tmpdir), p_purity_checks=0.5)
    assert second_cloud._instance_counter == 2
    with pytest.raises(BaseException):
        third_cloud = SharedStorage_P2P_Cloud(
            base_dir=tmpdir, p_purity_checks=0.25)

    P_Cloud_Implementation._reset()



def test_experiment():
    pass