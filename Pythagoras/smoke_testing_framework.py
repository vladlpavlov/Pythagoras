import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score

from Pythagoras.logging import *
from Pythagoras.caching import *
from Pythagoras.util import *
from Pythagoras.base import *

class DemoDB:
    """ An OOP wrapper for popular datasets"""
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


Boston = DemoDB("Boston")
California = DemoDB("California")

class RegressionSmokeTesting(LoggableObject):
    def __init__(self, regressor_to_test, cv = 7, scoring = "r2"):
        super().__init__()
        self.update_parent_logger()
        self.regressor_to_test = clone(regressor_to_test)
        self.cv = cv
        self.scoring = scoring
        for dataset in [Boston, California]:
            self.run_test(dataset)

    def run_test(self, dataset = Boston):
        log_message = "==>> Starting executing a smoke-test for a regressor "
        log_message += f"{self.regressor_to_test.__class__.__name__} with "
        log_message += f"cv={self.cv} and socring={self.scoring}. Sample "
        log_message += f"dataset is named {NeatStr.object_names(dataset)}"
        log_message += f"and its X's shape is {dataset.X.shape}."
        self.info(log_message)

        cv_scores = cross_val_score(
            self.regressor_to_test
            , dataset.X
            , dataset.y
            , cv=self.cv
            , scoring=self.scoring)
        log_message = "<<== Min, median and max values for CV-score are: "
        log_message += f"{min(cv_scores)}, "
        log_message += f"{median(cv_scores)}, "
        log_message += f"{max(cv_scores)}."
        self.info(log_message)


