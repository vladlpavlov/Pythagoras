import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from Pythagoras.util import *
from Pythagoras.base import *
from Pythagoras.smoke_testing_framework import *
from Pythagoras.logging import *
from Pythagoras.caching import *

class DemoDB:
    """ An OOP wrapper for popular SKLearn datasets"""
    def __init__(self, db: str):
        if db == "Boston":
            load_function = load_boston
            target_name = "MEDV"
        elif db == "California":
            load_function = fetch_california_housing
            target_name = "MedHouseVal"
        else:
            assert False

        dt = load_function()
        self.X = pd.DataFrame(data=dt.data, columns=dt.feature_names)
        self.y = pd.Series(data=dt.target, name=target_name)
        self.description = dt.DESCR

    def __str__(self):
        return self.description

    def __repr__(self):
        return self.description






