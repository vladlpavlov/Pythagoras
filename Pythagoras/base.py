import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from numpy import mean, median
from sklearn import clone
from sklearn.base import BaseEstimator
from sklearn.metrics import get_scorer
from sklearn.metrics._scorer import _BaseScorer
from sklearn.model_selection import BaseCrossValidator

from Pythagoras.util import *
from Pythagoras.logging import *
from Pythagoras.caching import *
from Pythagoras.splitters import *


class NotKnownType:
    """ Singleton for 'NotKnown' constant """

    not_known_single_instance = None

    def __new__(cls):
        if cls.not_known_single_instance is None:
            cls.not_known_single_instance = super().__new__(cls)
        return cls.not_known_single_instance

NotKnown = NotKnownType()


def update_param_if_supported(
        estimator: BaseEstimator
        ,param_name:str
        ,param_value:Any
        ) -> BaseEstimator:
    current_params = estimator.get_params()
    if param_name in current_params:
        new_params = {**current_params, param_name:param_value}
        return type(estimator)(**new_params)
    return type(estimator)(**current_params)


# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
class Learner(LoggableObject, BaseEstimator):
    pass


class Learner(BaseEstimator,LoggableObject):
    """ Abstract base class for estimators, w/ .val_fit() & .fit() methods.

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    def __init__(self
                 , *
                 , random_state = None
                 , root_logger_name: str = None
                 , logging_level: Union[str,int] = "WARNING"):
        super().__init__(
            root_logger_name = root_logger_name
            ,logging_level=logging_level )
        self.random_state = random_state

    def _preprocess_params(self):
        if self.root_logger_name is None:
            self.root_logger_name = "Pythagoras"
        assert isinstance(self.root_logger_name,str)

        if self.logging_level is None:
            self.logging_level = logging.WARNING
        assert isinstance(self.logging_level, (int,str))

    def __str__(self):
        if self.is_fitted():
            description = "Fitted"
        else:
            description = "Not fitted"
        description += f" {self.__class__.__name__} with the following parameters: "
        description += str(self.get_params())
        return description

    def _preprocess_X(self, X, sort_index:bool=True) -> pd.DataFrame:

        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(data=X, copy=True)
        else:
            X = deepcopy(X)

        X.columns = [str(c) for c in X.columns]

        assert len(X), "X can not be empty."
        assert len(X.columns) == len(set(X.columns)), (
            "Columns in X must have unique names.")

        X.columns = list(X.columns)

        if self.input_X_can_have_nans() is NotKnown:
            pass
        elif not self.input_X_can_have_nans():
            assert X.isna().sum().sum() == 0, "NaN-s are not allowed in X."

        if sort_index:
            X.sort_index(inplace=True)

        return X

    def _preprocess_Y(self, Y, sort_index:bool=True) -> pd.DataFrame:

        if not isinstance(Y, pd.DataFrame):
            Y = pd.DataFrame(data=Y, copy=True)
        else:
            Y = deepcopy(Y)

        Y.columns = [str(c) for c in Y.columns]

        assert len(Y), "When Y is present, its len() can't be zero."
        assert len(Y.columns) == len(set(Y.columns)), (
            "Columns in Y must have unique names.")

        Y.columns = list(Y.columns)

        if self.input_Y_can_have_nans() is NotKnown:
            pass
        elif not self.input_Y_can_have_nans():
            assert Y.isna().sum().sum() == 0, "NaN-s are not allowed in Y."

        if sort_index:
            Y.sort_index(inplace=True)

        return Y

    def _start_fitting(self
                       , X:Any
                       , Y:Any
                       , write_to_log:bool=True
                       , save_column_names:bool=True
                       ) -> Tuple[pd.DataFrame,pd.DataFrame]:

        self._preprocess_params()

        if write_to_log:
            log_message = f"==> Starting fitting {type(self).__name__} "
            log_message += f"using X = {type(X).__name__} named < "
            log_message += NeatStr.object_names(X, div_ch=" / ")
            log_message += f" > with the shape {X.shape}"
            if Y is not None:
                log_message += f", and Y = {type(Y).__name__} named < "
                log_message += NeatStr.object_names(Y, div_ch=" / ") + " >"
                log_message += f" > with the shape {Y.shape} "
            log_message += "."
            self.info(log_message)

        X = self._preprocess_X(X)
        if save_column_names:
            self.X_column_names_ = list(X.columns)
        self.n_features_in_ = len(X.columns)

        if Y is not None:
            Y = self._preprocess_Y(Y)
            assert len(X) == len(Y), "X and Y must have equal length."
            assert set(Y.index) == set(Y.index), (
                "X and Y must have equal indexes." )
            if save_column_names:
                self.Y_column_names_ = list(Y.columns)

        self.train_fit_idset_=set(X.index)
        self.full_fit_idset_ = self.train_fit_idset_

        return (X,Y)

    def _start_val_fitting(self
                           , X: Any
                           , Y: Any
                           , X_val: Any
                           , Y_val: Any
                           , write_to_log: bool = True
                           ) -> Tuple[pd.DataFrame, pd.DataFrame
                            , pd.DataFrame, pd.DataFrame]:
        if write_to_log:
            log_message = f"==> Starting val_fittig {type(self).__name__} "
            log_message += f"using X = {type(X).__name__} named < "
            log_message += NeatStr.object_names(X, div_ch=" / ")
            log_message += f" > with the shape {X.shape}"
            if Y is not None:
                log_message += f", and Y = {type(Y).__name__} named < "
                log_message += NeatStr.object_names(Y, div_ch=" / ") + " >"
                log_message += f" > with the shape {Y.shape} "
            log_message += ". Validation dataset contains "
            log_message += f"{len(X_val)} lines."
            self.info(log_message)

        X, Y = self._start_fitting(X, Y, write_to_log=False)
        X_val, Y_val = self._start_fitting(X_val, Y_val, write_to_log=False)
        assert sorted(list(X.columns)) == sorted(list(X_val.columns))
        if Y is not None:
            assert sorted(list(Y.columns)) == sorted(list(Y_val.columns))

        self.train_fit_idset_ = set(X.index)
        self.val_fit_idset_ = set(X_val.index)
        self.full_fit_idset_ = self.val_fit_idset_ | self.train_fit_idset_

        return X, Y, X_val, Y_val

    def _finish_fitting(self,write_to_log = True):
        if write_to_log:
            log_message = f"<== Fitting process has been finished."
            self.debug(log_message)

        return self


    def is_fitted(self) -> bool:
        return hasattr(self, "n_features_in_")

    def input_X_columns(self) -> List[str]:
        assert self.is_fitted()
        return self.X_column_names_

    def input_Y_columns(self) -> List[str]:
        assert self.is_fitted()
        return self.Y_column_names_

    def input_X_can_have_nans(self) -> bool:
        return NotKnown

    def input_Y_can_have_nans(self) -> bool:
        return NotKnown


class Mapper(Learner):
    """ Abstract base class for predictors / transformers, implements .map() .

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    def __init__(self
                 , *
                 , scoring = None
                 , splitting = None
                 , random_state = None
                 , root_logger_name: str = None
                 , logging_level = None
                 ) -> None:
        super().__init__(
            random_state = random_state
            ,root_logger_name = root_logger_name
            ,logging_level= logging_level )
        self.scoring = scoring
        self.splitting = splitting
        self._splitter = None

    def _preprocess_splitting_param(self):
        if self._splitter is None:
            self._splitter = self.splitting
            if self._splitter is None:
                self._splitter = AdaptiveKFold()
            elif isinstance(self._splitter, int):
                self._splitter = AdaptiveKFold(n_splits=self._splitter)
            else:
                assert isinstance(self._splitter, BaseCrossValidator)

    def _preprocess_scoring_param(self):
        scorer = self.scoring
        if scorer is None:
            scorer = "r2"  # TODO: add support for various scorers
        scorer = get_scorer(scorer)
        self._scorer = scorer

    def _preprocess_params(self):
        super()._preprocess_params()
        self._preprocess_scoring_param()
        self._preprocess_splitting_param()

    def map(self,X:pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def _start_mapping(self
                       , X: pd.DataFrame
                       , write_to_log: bool = True
                       ) -> pd.DataFrame:

        if write_to_log:
            log_message = f"==> Starting mapping process "
            log_message += f"using X = {type(X).__name__} named < "
            log_message += NeatStr.object_names(X, div_ch=" / ")
            log_message += f" > with the shape {X.shape}."
            self.info(log_message)

        assert self.is_fitted()
        X = self._preprocess_X(X, sort_index=False)
        self.pre_mapping_X_idx_ = deepcopy(X.index)

        if self.input_X_columns() is NotKnown:
            pass
        else:
            assert set(self.input_X_columns()) <= set(X)
            X = deepcopy(X[self.input_X_columns()])

        return X

    def _finish_mapping(self
                        , Z: pd.DataFrame
                        , write_to_log: bool = True
                        ) -> pd.DataFrame:

        n_nans = Z.isna().sum().sum()

        if write_to_log:
            log_message = f"<== Mapping has been created with the shape "
            log_message += f"{Z.shape}."
            if n_nans:
                log_message += f" It contains {n_nans} NaN-s."
            self.info(log_message)

        assert len(Z)
        assert len(Z) == len(self.pre_mapping_X_idx_)
        assert set(Z.index) == set(self.pre_mapping_X_idx_)

        if self.output_Z_can_have_nans() is NotKnown:
            pass
        elif not self.output_Z_can_have_nans():
            assert n_nans == 0

        if self.output_Z_columns() is not NotKnown:
            assert set(Z.columns) == set(self.output_Z_columns())

        Z = Z.reindex(index=self.pre_mapping_X_idx_) # TODO: Check whether it works as intended

        return Z

    def predict(self,X:pd.DataFrame)->pd.DataFrame:
        return self.map(X)

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.map(X)

    def get_scorer(self) -> _BaseScorer:
        self._preprocess_scoring_param()
        scorer = self._scorer
        return scorer

    def get_splitter(self) -> BaseCrossValidator:
        self._preprocess_splitting_param()
        splitter = self._splitter
        return splitter

    def get_n_splits(self) -> int:
        self._preprocess_splitting_param()
        return self._splitter.get_n_splits()

    def output_Z_columns(self) -> List[str]:
        return NotKnown

    def output_Z_can_have_nans(self) -> bool:
        return NotKnown

    def output_Z_is_numeric_only(self) -> bool:
        return NotKnown

    def is_leakproof(self) -> bool:
        return False

