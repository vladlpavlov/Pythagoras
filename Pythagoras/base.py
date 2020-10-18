import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from numpy import mean, median
from sklearn import clone
from sklearn.base import BaseEstimator
from sklearn.model_selection import cross_val_score, RepeatedKFold

from Pythagoras.util import *
from Pythagoras.logging import *
from Pythagoras.caching import *


class NotProvidedType:
    not_provided_single_instance = None
    def __new__(cls):
        if cls.not_provided_single_instance is None:
            cls.not_provided_single_instance = super().__new__(cls)
        return cls.not_provided_single_instance

NotProvided = NotProvidedType()


# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
class PEstimator(LoggableObject, BaseEstimator):
    pass

class PEstimator(LoggableObject,BaseEstimator):
    """ Abstract base class for all estimators (classes with fit() method).

        Warning: This class should not be used directly. Use derived classes
        instead.
        """

    def __init__(self
                 , *
                 , parent_logger_name: str = "Pythagoras"
                 , new_logging_level = None):
        super().__init__(parent_logger_name = parent_logger_name )
        self.update_parent_logger(new_logging_level = new_logging_level)


    def _preprocess_X(self, X:pd.DataFrame, sort_index=True) -> pd.DataFrame:

        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(data=X, copy=True)
        else:
            X = deepcopy(X)

        X.columns = [str(c) for c in X.columns]

        assert len(X), "X can not be empty."
        assert len(X.columns) == len(set(X.columns)), (
            "Input columns must have unique names.")

        X.columns = list(X.columns)

        if self.input_can_have_nans() is NotProvided:
            pass
        elif not self.input_can_have_nans():
            assert X.isna().sum().sum() == 0, "NaN-s are not allowed."

        if sort_index:
            X.sort_index(inplace=True)

        return X

    def _preprocess_y(self, y:pd.Series, sort_index=True) -> pd.Series:
        # TODO: add support for multi-target outputs (y as a DataFrame)
        if isinstance(y, pd.Series):
            y = deepcopy(y)
        else:
            y = pd.Series(y, copy=True)

        if y.name is None:
            y.name = "y_target"

        assert y.isna().sum() == 0
        if sort_index:
            y.sort_index(inplace=True)

        return y


    def start_fitting(self
            ,X:Any
            ,y:Any
            ,write_to_log:bool=True
            ,save_target_name:bool=True
            ) -> Tuple[pd.DataFrame,pd.Series]:
        if write_to_log:
            log_message = f"==> Starting fittig {type(self).__name__} "
            log_message += f"using a {type(X).__name__} named < "
            log_message += NeatStr.object_names(X, div_ch=" / ")
            log_message += f" > with the shape {X.shape}, "
            log_message += f"and a {type(y).__name__} named < "
            log_message += NeatStr.object_names(y, div_ch=" / ") + " >."
            self.info(log_message)

        X = self._preprocess_X(X)

        if y is not None:
            y = self._preprocess_y(y)
            assert len(X) == len(y), "X and y must have equal length."
            assert set(X.index) == set(y.index)
            if save_target_name:
                self.target_name_ = y.name

        return (X,y)

    def start_val_fitting(self
                        , X: Any
                        , y: Any
                        , X_val: Any
                        , y_val: Any
                        , write_to_log: bool = True
                        ) -> Tuple[pd.DataFrame, pd.Series
                            , pd.DataFrame, pd.Series]:
        if write_to_log:
            log_message = f"==> Starting val_fittig {type(self).__name__} "
            log_message += f"using a {type(X).__name__} named < "
            log_message += NeatStr.object_names(X, div_ch=" / ")
            log_message += f" > with the shape {X.shape}, "
            log_message += f"and a {type(y).__name__} named < "
            log_message += NeatStr.object_names(y, div_ch=" / ") + " >. "
            log_message += "Validation dataset contains "
            log_message += f"{len(X_val)} lines."
            self.info(log_message)

        X, y = super().start_fitting(X, y, write_to_log=False)
        X_val, y_val = super().start_fitting(X_val, y_val, write_to_log=False)
        assert list(X.columns) == list(X_val.columns)
        assert y.name == y_val.name
        self.target_name_ = y.name
        self.min_med_max_ = (min(y), percentile50(y), max(y))
        return X, y, X_val, y_val

    def is_fitted(self) -> bool: ### ???????
        raise NotImplementedError

    def input_columns(self) -> List[str]:
        return NotProvided

    def input_can_have_nans(self) -> bool:
        return NotProvided

    def output_can_have_nans(self) -> bool:
        return NotProvided


Estimator = Union[BaseEstimator, PEstimator]

def update_param_if_supported(
        estimator: Estimator
        ,param_name:str
        ,param_value:Any
        ) -> Estimator:
    current_params = estimator.get_params()
    if param_name in current_params:
        new_params = {**current_params, param_name:param_value}
        return type(estimator)(**new_params)
    return type(estimator)(**current_params)


class PRegressor(PEstimator):
    """ Abstract base class for all Pythagoras regressors.

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    target_name_: Optional[str] # TODO: add suport for multi-target regressors
    prediction_index_:Optional[pd.Series]
    min_med_max_:Tuple[float,float,float]

    def __init__(self
                 , *
                 , parent_logger_name: str = "Pythagoras"
                 , new_logging_level = None):
        super().__init__(parent_logger_name = "Pythagoras"
                 , new_logging_level = new_logging_level)

    def start_fitting(self
                      , X: Any
                      , y: Any
                      , write_to_log: bool = True
                      , save_target_name: bool = True
                      ) -> Tuple[pd.DataFrame, pd.Series]:

        X, y = super().start_fitting(X, y, write_to_log,save_target_name)

        self.min_med_max_ = (min(y), percentile50(y), max(y))

        return X, y

    def start_val_fitting(self
                          , X: Any
                          , y: Any
                          , X_val: Any
                          , y_val: Any
                          , write_to_log: bool = True
                          ) -> Tuple[pd.DataFrame, pd.Series
                                , pd.DataFrame, pd.Series]:

        X, y, X_val, y_val = super().start_val_fitting(
            X, y, X_val, y_val,write_to_log=write_to_log)

        self.min_med_max_ = (min(y), percentile50(y), max(y))

        return X, y, X_val, y_val

    def predict(self, X:pd.DataFrame) -> pd.Series:
        raise NotImplementedError

    def start_predicting(self
                         , X: pd.DataFrame
                         , write_to_log: bool = True
                         ) -> pd.DataFrame:

        if write_to_log:
            log_message = f"==> Starting generating predictions "
            log_message += f"using a {type(X).__name__} named < "
            log_message += NeatStr.object_names(X, div_ch=" / ")
            log_message += f" > with the shape {X.shape}."
            self.info(log_message)

        assert self.is_fitted()
        X = self._preprocess_X(X, sort_index=False)
        self.prediction_index_ = deepcopy(X.index)

        if self.input_columns() is NotProvided:
            pass
        else:
            assert set(self.input_columns()) <= set(X)
            X = deepcopy(X[self.input_columns()])

        return X

    def finish_predicting(self
                          , y: pd.Series
                          , write_to_log: bool = True
                          ) -> pd.Series:

        n_val = len(y)
        p_min_med_max = (min(y), percentile50(y), max(y))
        n_nans = y.isna().sum()

        if write_to_log:
            log_message = f"<== Predictions for {y.name} have been created. "
            log_message += f"The result contains {n_val} values "
            log_message += f"with {n_nans} NaN-s, with the following "
            log_message += f"min, median, max: {p_min_med_max}; "
            log_message += f"while the taining data had {self.min_med_max_}."
            self.info(log_message)

        assert len(y)
        assert len(y) == len(self.prediction_index_)

        if self.output_can_have_nans() is NotProvided:
            pass
        elif not self.output_can_have_nans():
            assert n_nans == 0

        y.name = self.target_name_
        y=y.reindex(index=self.prediction_index_) # TODO: Check whether it works as intended
        #y.index = self.prediction_index_
        return y


class PFeatureMaker(PEstimator):

    def __init__(self
                 , *
                 , parent_logger_name: str = "Pythagoras"
                 , new_logging_level = None):
        super().__init__(parent_logger_name=parent_logger_name
                         ,new_logging_level=new_logging_level)

    def output_columns(self) -> List[str]:
        return NotProvided

    def start_transforming(self
                           , X: pd.DataFrame
                           , write_to_log: bool = True
                           ) -> pd.DataFrame:
        if write_to_log:
            log_message = f"==> Starting generating features "
            log_message += f"using a {type(X).__name__} named < "
            log_message += NeatStr.object_names(X, div_ch=" / ")
            log_message += f" > with the shape {X.shape}."
            self.info(log_message)

        assert self.is_fitted()
        X = self._preprocess_X(X)

        if self.input_columns() is NotProvided:
            pass
        else:
            assert set(self.input_columns()) <= set(X)
            X = deepcopy(X[self.input_columns()])

        return X

    def finish_transforming(self
                            , X: pd.DataFrame
                            , write_to_log: bool = True
                            ) -> pd.DataFrame:
        if write_to_log:
            log_message = f"<== {len(X.columns)} features "
            log_message += "have been generated/returned."
            self.info(log_message)

        assert len(X)
        assert len(set(X.columns)) == len(X.columns)

        if self.output_columns() is NotProvided:
            pass
        else:
            assert set(X.columns) == set(self.output_columns())

        if self.output_can_have_nans() is NotProvided:
            pass
        elif not self.output_can_have_nans():
            n_NaNs = X.isna().sum().sum()
            assert n_NaNs==0, f"{n_NaNs} NaN-s found, while expecting 0"

        return X

    def fit_transform(self
            ,X:pd.DataFrame
            ,y:Optional[pd.Series]=None
            ) -> pd.DataFrame:
        raise NotImplementedError
