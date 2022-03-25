from pythagoras import *
from moto import mock_s3

def test_SharedStorage_P2P_Cloud(tmpdir):
    my_cloud = SharedStorage_P2P_Cloud(shared_dir_name=tmpdir)

    @my_cloud.add_pure_function
    def fff():
        return int(1)

    assert len(my_cloud.functions)==1

    for i in range(4): assert fff() == 1
    assert len(my_cloud.value_store) == len(my_cloud.func_execution_results) == 1

    @my_cloud.add_pure_function
    def ggg(a:int):
        return int(a*a)

    assert len(my_cloud.functions) == 2

    for i in range(4): assert ggg(a=1) == 1
    assert len(my_cloud.value_store) +1 == len(my_cloud.func_execution_results) == 2

    for i in range(4): assert ggg(a=2) == 4
    assert len(my_cloud.value_store) == len(my_cloud.func_execution_results) == 3

    for i in range(4):  assert ggg(a=3) == 9
    assert len(my_cloud.value_store) == 5 == len(my_cloud.func_execution_results) +1

    for i in range(4):
        assert ggg.parallel(kw_args(a=i) for i in range(10)) == [i*i for i in range(10)]
