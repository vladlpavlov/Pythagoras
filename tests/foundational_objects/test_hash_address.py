import pytest
import pandas as pd
from pythagoras.utils.global_state_initializer import (
    initialize, _clean_global_state)

from pythagoras.foundational_objects import *


def test_value_address_basic(tmpdir):
        """Test ValueAddress constructor and basis functions."""
        _clean_global_state()
        initialize(base_dir=tmpdir, island_name="test", cloud_type="local")
        samples_to_test = ["something", 10, 10.0, 10j, True, None
            , (1,2,3), [1,2,3], {1,2,3}, {1:2, 3:4}
            , pd.DataFrame([[1,2.005],[-3,"QQQ"]])]
        for sample in samples_to_test:
            assert ValueAddress(sample) == ValueAddress(sample)
            assert ValueAddress(sample) != ValueAddress("something else")
            assert ValueAddress(sample).ready()
            restored_sample = deepcopy(ValueAddress(sample).get())
            if type(sample) == pd.DataFrame:
                assert sample.equals(restored_sample)
            else:
                assert ValueAddress(sample).get() == sample


def test_packed_kwargs(tmpdir):
    """Test PackedKwArgs constructor and basic functions."""
    _clean_global_state()
    initialize(base_dir=tmpdir, island_name="test", cloud_type="local")

    sampe_dict = { "e": 0, "c":1, "b":2, "a":3}
    assert list(sampe_dict.keys()) != sorted(sampe_dict.keys())

    pka = PackedKwArgs(**sampe_dict)
    assert list(pka.keys()) == sorted(pka.keys())

    for k in pka:
        assert pka[k] == ValueAddress(sampe_dict[k])

    assert pka.unpack() == sampe_dict
    assert pka == PackedKwArgs(**pka.unpack())