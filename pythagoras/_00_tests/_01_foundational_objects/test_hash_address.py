from copy import deepcopy

import pandas as pd
from pythagoras._07_mission_control.global_state_management import (
    initialize, _clean_global_state)

from pythagoras._01_foundational_objects import *


def test_value_address_basic(tmpdir):
        """Test ValueAddr constructor and basis functions."""
        _clean_global_state()
        initialize(base_dir=tmpdir, n_background_workers = 0)
        samples_to_test = ["something", 10, 10.0, 10j, True, None
            , (1,2,3), [1,2,3], {1,2,3}, {1:2, 3:4}
            , pd.DataFrame([[1,2.005],[-3,"QQQ"]])]
        for sample in samples_to_test:
            assert ValueAddr(sample) == ValueAddr(sample)
            assert ValueAddr(sample) != ValueAddr("something else")
            assert ValueAddr(sample).ready
            restored_sample = deepcopy(ValueAddr(sample).get())
            if type(sample) == pd.DataFrame:
                assert sample.equals(restored_sample)
            else:
                assert ValueAddr(sample).get() == sample
