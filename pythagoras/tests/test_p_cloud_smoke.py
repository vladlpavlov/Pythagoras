import ast
import gc


from pythagoras import *
import pytest

def ggg_sp(a:int):
    from time import sleep
    sleep(3)
    return int(a*a)

def ggg2_sp(x:int,y:float):
    from time import sleep
    sleep(3)
    return int(x*x*y)

def test_SharedStorage_P2P_Cloud_func1args_sp(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir)

    global ggg_sp
    ggg_sp = my_cloud.cloudize_function(ggg_sp)
    assert ggg_sp._sync_subprocess_v(a=5) == 25

    global ggg2_sp
    ggg2_sp = my_cloud.cloudize_function(ggg2_sp)
    assert ggg2_sp._sync_subprocess_v(x=2,y=3) == 12

    P_Cloud_Implementation._reset()

def ooo_asp(a:int):
    from time import sleep
    sleep(10)
    return int(a*a)

def test_SharedStorage_P2P_Cloud_func1args_asp(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir, p_purity_checks=0.5)

    global ooo_asp
    ooo_asp = my_cloud.cloudize_function(ooo_asp)

    addr = ooo_asp._async_subprocess_a(a=7)
    assert addr.get(timeout=20 ) == 49

    P_Cloud_Implementation._reset()


def fff():
    return int(1)

def ggg(a:int):
    from time import sleep
    return int(a*a)

def test_SharedStorage_P2P_Cloud_func1args(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir, p_purity_checks=0.5)

    global fff
    fff = my_cloud.cloudize_function(fff)

    assert len(my_cloud.original_functions) == len(my_cloud.cloudized_functions) == 1

    for i in range(4): assert fff() == 1
    assert len(my_cloud.value_store) == 4
    assert len(my_cloud.func_output_store)  == 1

    global ggg
    ggg = my_cloud.cloudize_function(ggg)

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
        assert ggg._sync_group_inpocess_kwargss_v([kw_args(a=i) for i in range(10)]) == (
            [i*i for i in range(10)])

    addr = PFuncOutputAddress("ggg", kw_args(a=100))
    my_cloud.sync_local_inprocess_function_call(addr)
    value_store_len = len(my_cloud.value_store)

    del ggg, fff, my_cloud

    P_Cloud_Implementation._reset()


    my_new_cloud = SharedStorage_P2P_Cloud(
        base_dir=tmpdir
        , p_purity_checks=0.5
        , restore_from = addr)

    assert ggg(a=100) == 10000

    for i in range(4):
        assert ggg._sync_group_inpocess_kwargss_v([kw_args(a=i) for i in range(10)]) == (
            [i*i for i in range(10)])

    assert len(my_new_cloud.value_store) == value_store_len

    P_Cloud_Implementation._reset()



def hihihi(*, x: int, y: int):
    return x + 100 * y

def test_SharedStorage_P2P_Cloud_func2args(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir, p_purity_checks=0.5)

    global hihihi
    hihihi = my_cloud.cloudize_function(hihihi)

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
    lyslyslya = my_cloud.cloudize_function(lyslyslya)


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
        base_dir=tmpdir)
    second_cloud = SharedStorage_P2P_Cloud(
        base_dir=tmpdir)
    assert second_cloud._instance_counter == 2

    with pytest.raises(BaseException):
        third_cloud = SharedStorage_P2P_Cloud(
            base_dir=tmpdir
            , persist_config_update=dict(
                p_idempotency_checks = 0.987654321))

    P_Cloud_Implementation._reset()


