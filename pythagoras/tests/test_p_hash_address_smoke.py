from pythagoras.p_cloud import SharedStorage_P2P_Cloud, PFuncOutputAddress, P_Cloud_Implementation

from pythagoras import PValueAddress
import pandas as pd
import numpy as np


def hihihi():
    pass


simple_test_cases = [
    {"obj": "", "prefix_tests": ["str"], "descriptor_tests": ["len_0"]}
    , {"obj": "0123456789", "prefix_tests": ["str"], "descriptor_tests": ["len_10"]}
    , {"obj": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "prefix_tests": ["list"], "descriptor_tests": ["len_10"]}
    , {"obj": {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, "prefix_tests": ["set"], "descriptor_tests": ["len_10"]}
    , {"obj": {0:0, 1:1, 2:2, 3:3}, "prefix_tests": ["dict"], "descriptor_tests": ["len_4"]}
    , {"obj": 100, "prefix_tests": ["int"], "descriptor_tests":[]}
    , {"obj": 0.01, "prefix_tests": ["float"], "descriptor_tests":[]}
    , {"obj": hihihi, "prefix_tests": ["hihihi", "function"], "descriptor_tests":[]}
    , {"obj":pd.DataFrame({"a":[1,2,3]}), "prefix_tests":["pandas", "DataFrame"], "descriptor_tests":["shape","3_x_1"]}
    , {"obj": np.array([[1, 2], [3, 4]]), "prefix_tests": ["numpy", "ndarray"], "descriptor_tests": ["shape", "2_x_2"]}
]


def test_PHashAddress(tmpdir):
    cloud = SharedStorage_P2P_Cloud(tmpdir)
    all_hash_ids = set()
    for a_case in simple_test_cases:
        address = PValueAddress(a_case["obj"])

        assert len(address) == 2 + int(bool(address.descriptor))
        assert len(list(address)) == 2 + int(bool(address.descriptor))
        assert address == PValueAddress(address)
        assert address != PValueAddress(list(address))

        prfx_str = list(address)[0]
        grpid_str = list(address)[1]
        assert isinstance(prfx_str, str)
        for substr in a_case["prefix_tests"]:
            assert substr in prfx_str
            assert substr in repr(address)
        for substr in a_case["descriptor_tests"]:
            assert substr in grpid_str
            assert substr in repr(address)

        hash_id_str = list(address)[1+int(bool(address.descriptor))]
        assert isinstance(hash_id_str, str)
        assert len(hash_id_str) == 64
        assert len(set(hash_id_str)) <= 16
        assert hash_id_str not in all_hash_ids
        all_hash_ids.add(hash_id_str)

    P_Cloud_Implementation._reset()


def myau(n:int):
    return n+1

def test_constructors(tmpdir):
    cloud = SharedStorage_P2P_Cloud(tmpdir)
    val = dict(a=1,b=2)
    address = PValueAddress(val)
    new_address = PValueAddress.from_strings(
        prefix=address.prefix, descriptor=address.descriptor, hash_value=address.hash_value)
    assert address == new_address

    global myau
    myau = cloud.publish(myau)

    f_address = myau.async_remote(n=100)
    new_f_address = PFuncOutputAddress.from_strings(
        prefix=f_address.prefix, descriptor=f_address.descriptor, hash_value=f_address.hash_value)
    assert f_address == new_f_address

    P_Cloud_Implementation._reset()


