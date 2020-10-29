import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from sklearn.base import is_regressor
from sklearn.linear_model import LinearRegression

from Pythagoras.misc_utils import *
from Pythagoras.base import *
from Pythagoras.not_known import *
from Pythagoras.logging import *
from Pythagoras.caching import *

class DemoDB:
    """ An OOP wrapper for popular SKLearn datasets"""
    def __init__(self, db_name: str):
        self.name = db_name
        if db_name == "Boston":
            load_function = load_boston
            target_name = "MEDV"
        elif db_name == "California":
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


class MapperFromSKLRegressor(Mapper):
    """A wrapper for SKLearn regressors
    """

    def __init__(self
            , base_regressor = LinearRegression()
            , defaults:LearningContext = LearningContext()
            , scoring = None
            , cv_splitting = 5
            , index_filter: Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
            , X_col_filter: Optional[ColumnFilter] = None
            , Y_col_filter: Optional[ColumnFilter] = None
            , random_state = None
            , root_logger_name: str = "Pythagoras"
            , logging_level = logging.WARNING) -> None:

        _estimator_type = "regressor"

        super().__init__(
            defaults = defaults
            , scoring=scoring
            , cv_splitting = cv_splitting
            , index_filter = index_filter
            , X_col_filter = X_col_filter
            , Y_col_filter = Y_col_filter
            , random_state = random_state
            , root_logger_name = root_logger_name
            , logging_level=logging_level)

        self.base_regressor = base_regressor

        if not isinstance(base_regressor, BaseEstimator):
            log_message = f"base_regressor has type={type(base_regressor)}, "
            log_message += f"which is not inherited from BaseEstimator."
            self.warning(log_message)

        if isinstance(base_regressor, Mapper):
            log_message = f"base_regressor has type={type(base_regressor)}, "
            log_message += f"which is already inherited from Mapper."
            self.warning(log_message)

    def _preprocess_params(self):
        super()._preprocess_params()
        assert is_regressor(self.base_regressor)
        self.base_regressor = clone(self.base_regressor)


    def fit(self,X:pd.DataFrame,Y:pd.DataFrame,**kwargs):
        (X,Y) = self._start_fitting(X, Y)
        self.base_regressor.fit(X,Y,**kwargs)
        self._finish_fitting()
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


def get_mapper(estimator:BaseEstimator) -> Mapper:
    if isinstance(estimator, Mapper):
        return estimator
    elif is_regressor(estimator):
        return MapperFromSKLRegressor(base_regressor = estimator)
    else:
        error_message = f"An Estimator has type {type(estimator)}, "
        error_message += f"which curently can't be automatically "
        error_message += f"to a Mapper."
        raise NotImplementedError("")


