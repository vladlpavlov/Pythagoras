from pythagoras import *
from moto import mock_s3

def test_SharedStorage_P2P_Cloud_func1args(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(shared_dir_name=tmpdir)

    @my_cloud.add_pure_function
    def fff():
        return int(1)

    assert len(my_cloud.functions)==1

    for i in range(4): assert fff() == 1
    assert len(my_cloud.value_store) == len(my_cloud.func_output_store) == 1

    @my_cloud.add_pure_function
    def ggg(a:int):
        return int(a*a)

    assert len(my_cloud.functions) == 2

    for i in range(4): assert ggg(a=1) == 1
    assert len(my_cloud.value_store) + 1 == len(my_cloud.func_output_store) == 2

    for i in range(4): assert ggg(a=2) == 4
    assert len(my_cloud.value_store) == len(my_cloud.func_output_store) == 3

    for i in range(4):  assert ggg(a=3) == 9
    assert len(my_cloud.value_store) == 5 == len(my_cloud.func_output_store) + 1

    for i in range(4):
        assert ggg.parallel(kw_args(a=i) for i in range(10)) == [i*i for i in range(10)]


def test_SharedStorage_P2P_Cloud_func2args(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(shared_dir_name=tmpdir)

    @my_cloud.add_pure_function
    def hihihi(*, x: int, y: int):
        return x + 100 * y

    assert hihihi(x=1, y=2) == hihihi(x=1, y=2) == hihihi(y=2, x=1)

    assert len(my_cloud.value_store) == 3
    assert len(my_cloud.func_output_store) == 1


def test_SharedStorage_P2P_Cloud_func3args(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(shared_dir_name=tmpdir)

    @my_cloud.add_pure_function
    def lyslyslya(*, x: float, y: float, z:float):
        return x + 100 * y + z*10_000

    assert lyslyslya(x=1, y=2, z=3) == lyslyslya(z=3, x=1, y=2)
    assert lyslyslya(x=1, y=2, z=3) == lyslyslya(z=3, y=2, x=1)
    assert lyslyslya(y=2, x=1, z=3) == lyslyslya(z=3, y=2, x=1)

    assert len(my_cloud.value_store) == 4
    assert len(my_cloud.func_output_store) == 1