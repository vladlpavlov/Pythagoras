import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from sklearn.linear_model import LinearRegression

from Pythagoras.util import *
from Pythagoras.base import *
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
        self.Y = pd.Series(data=dt.target, name=target_name)
        self.y = self.Y
        self.description = dt.DESCR

    def __str__(self):
        return self.description

    def __repr__(self):
        return self.description


class SKLearnRegressor(Mapper):
    """A wrapper for SKLearn regressors
    """

    def __init__(self
                 , base_regressor = LinearRegression()
                 , scoring = "r2"
                 , splitting = 5
                 , random_state = None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level = logging.WARNING) -> None:

        _estimator_type = "regressor"

        super().__init__(
            scoring=scoring
            , splitting = splitting
            , random_state = random_state
            , root_logger_name = root_logger_name
            , logging_level=logging_level)
        self.base_regressor = base_regressor

    def _preprocess_params(self):
        super()._preprocess_params()
        self.base_regressor = clone(self.base_regressor)

    def fit(self,X:pd.DataFrame,Y:pd.DataFrame,**kwargs):
        (X,Y) = self._start_fitting(X, Y)
        self.base_regressor.fit(X,Y,**kwargs)
        return self

    def map(self,X:pd.DataFrame) -> pd.DataFrame:
        X = self._start_mapping(X)
        Z = self.base_regressor.predict(X)
        Z = pd.DataFrame(data=Z, index=X.index, columns=self.Y_column_names_)
        Z = self._finish_mapping(Z)
        return Z

    def score(self,X,Y,**kwargs) -> float:
        assert self.is_fitted()
        scorer = self.get_scorer()
        result = scorer(self.base_regressor,X,Y,kwargs)
        return result

    def _get_tags(self):
        return self.base_regressor._get_tags()





