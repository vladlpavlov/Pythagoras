from copy import deepcopy

import pandas as pd
from pythagoras._05_mission_control.global_state_management import (
    initialize, _clean_global_state)

from pythagoras._01_foundational_objects import *


def test_value_address_basic(tmpdir):
        """Test ValueAddress constructor and basis functions."""
        _clean_global_state()
        initialize(base_dir=tmpdir, default_island_name="test", cloud_type="local")
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
