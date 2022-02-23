from Pythagoras import PHashAddress
import pandas as pd
import numpy as np


def hihihi():
    pass


simple_cases = [
    {"obj": "", "tests": ["str", "_len_0"]}
    , {"obj": "0123456789", "tests": ["str", "_len_10"]}
    , {"obj": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "tests": ["list", "_len_10"]}
    , {"obj": {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, "tests": ["set", "_len_10"]}
    , {"obj": {0:0, 1:1, 2:2, 3:3}, "tests": ["dict", "_len_4"]}
    , {"obj": 100, "tests": ["int"]}
    , {"obj": 0.01, "tests": ["float"]}
    , {"obj": hihihi, "tests": ["hihihi", "function"]}
    , {"obj":pd.DataFrame({"a":[1,2,3]}), "tests":["pandas", "DataFrame","shape","3_x_1"]}
    , {"obj": np.array([[1, 2], [3, 4]]), "tests": ["numpy", "ndarray", "shape", "2_x_2"]}
]


def test_PHashAddress():
    all_hash_ids = set()
    for case in simple_cases:
        address = PHashAddress(case["obj"])
        assert len(address) == 2
        assert len(list(address)) == 2
        assert address == PHashAddress(address)
        assert address != PHashAddress(list(address))

        prfx_str = list(address)[0]
        assert isinstance(prfx_str, str)
        for substr in case["tests"]:
            assert substr in prfx_str
            assert substr in repr(address)

        hash_id_str = list(address)[1]
        assert isinstance(hash_id_str, str)
        assert len(hash_id_str) == 64
        assert len(set(hash_id_str)) <= 16
        assert hash_id_str not in all_hash_ids
        all_hash_ids.add(hash_id_str)
