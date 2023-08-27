import pytest
import pandas as pd
import pythagoras

from persidict import FileDirDict
from pythagoras.NEW_hash_address import set_value_store
from pythagoras.NEW_hash_address import HashAddress, ValueAddress, PackedKwArgs


class TestHashAddress:
    def test_constructor(self,tmpdir):
        """Test HashAddress constructor."""
        set_value_store(FileDirDict(tmpdir))
        with pytest.raises(TypeError):
            ha = HashAddress("something")

class TestValueAddress:
    def test_constructor(self,tmpdir):
        """Test ValueAddress constructor and basis functions."""
        set_value_store(FileDirDict(tmpdir))
        samples_to_test = ["something", 10, 10.0, 10j, True, None
            , (1,2,3), [1,2,3], {1,2,3}, {1:2, 3:4}
            , pd.DataFrame([[1,2.005],[-3,"QQQ"]])]
        for sample in samples_to_test:
            assert ValueAddress(sample) == ValueAddress(sample)
            assert ValueAddress(sample) != ValueAddress("something else")
            assert ValueAddress(sample).ready()
            restored_sample = ValueAddress(sample).get()
            if type(sample) == pd.DataFrame:
                assert sample.equals(restored_sample)
            else:
                assert ValueAddress(sample).get() == sample

class TestPackedKwArgs:
    def test_constructor(self, tmpdir):
        """Test PackedKwArgs constructor and basic functions."""
        set_value_store(FileDirDict(tmpdir))

        sampe_dict = { "e": 0, "c":1, "b":2, "a":3}
        assert list(sampe_dict.keys()) != sorted(sampe_dict.keys())

        pka = PackedKwArgs(**sampe_dict)
        assert list(pka.keys()) == sorted(pka.keys())

        for k in pka:
            assert pka[k] == ValueAddress(sampe_dict[k])

        assert pka.unpack() == sampe_dict
        assert pka == PackedKwArgs(**pka.unpack())
