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


# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
class Learner(LoggableObject, BaseEstimator):
    pass


class ColumnFilter:
    def __init__(self, names:Optional[List[str]]=None) -> None:
        super().__init__()
        self.names = names

    def filter(self, df:Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
        """ Default pass-through implementation"""
        if df is None:
            return None
        elif self.names is None:
            return df
        else:
            columns = list(df.columns)
            assert set(self.names) <= set(columns)
            return df[self.names]

class IndexFilter:
    def __init__(self, max_samples=None, random_state=None) -> None:
        super().__init__()
        assert isinstance(max_samples, (int, float, type(None)))
        if isinstance(max_samples, float):
            assert 0.0 < max_samples <= 1.0
        elif isinstance(max_samples, int):
            assert 1 <= max_samples
        self.max_samples = max_samples
        self.random_state = random_state

    def filter(self,X:pd.DataFrame, Y:Optional[pd.DataFrame]=None
               ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        if self.max_samples is None:
            return (X,Y)
        elif isinstance(self.max_samples, float):
            if self.max_samples == 1.0: return (X,Y)
            n_samples = max( 1 , int(len(X)*self.max_samples) )
        else:
            if (self.max_samples >= len(X)): return (X,Y)
            n_samples = min( self.max_samples , len(X) )

        X_samples = X
        Y_samples = Y

        splitter = AdaptiveShuffleSplit(
            train_size=n_samples, random_state=self.random_state)
        for (samples_idx,_) in splitter.split(X, Y):
            X_samples = X.iloc[samples_idx]
            Y_samples = None if (Y is None) else Y.iloc[samples_idx]
            break

        return (X_samples, Y_samples)


class LearnersContext:
    root_logger_name:Optional[str]
    logging_level:Union[int,str,type(None)]

    random_state: Any

    index_filer:IndexFilter
    X_col_filter:ColumnFilter
    Y_col_filter:ColumnFilter

    scoring:Any

    cv_splitting:Any

    def __init__(self
            ,*
            ,random_state = None
            ,root_logger_name = None
            ,logging_level = None
            ,index_filter:Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
            ,X_col_filter:Optional[ColumnFilter] = None
            ,Y_col_filter:Optional[ColumnFilter] = None
            ,scoring:Union[str,Callable[..., float], None] = None
            ,cv_splitting:Union[
                BaseCrossValidator, AdaptiveSplitter, int, None] = None
            ) -> None:
        self.random_state = None
        self.random_state = self.get_random_state(random_state)

        self.root_logger_name = "Pythagoras"
        self.root_logger_name = self.get_root_logger_name(root_logger_name)

        self.logging_level = logging.WARNING
        self.logging_level = self.get_logging_level(logging_level)

        self.index_filter = IndexFilter()
        self.index_filter = self.get_index_filter(index_filter)

        self.X_col_filter = ColumnFilter()
        self.X_col_filter = self.get_X_col_filter(X_col_filter)

        self.Y_col_filter = ColumnFilter()
        self.Y_col_filter = self.get_Y_col_filter(Y_col_filter)

        self.scoring = get_scorer("r2")
        self.scoring = self.get_scoring(scoring)

        self.cv_splitting = AdaptiveKFold(n_splits=5)
        self.cv_splitting = self.get_cv_splitting(cv_splitting)


    def get_random_state(self, input_value):
        if input_value is None:
            return self.random_state
        else:
            return input_value


    def get_root_logger_name(self
            , input_value:Optional[str]
            ) -> Optional[str]:
        if input_value is None:
            return self.root_logger_name
        else:
            assert isinstance(input_value, str)
            return input_value


    def get_logging_level(self, input_value):
        if input_value is None:
            return self.logging_level
        else:
            assert isinstance(input_value, (str, int))
            return input_value


    def get_index_filter(self
            ,input_value:Union[IndexFilter,int,float,type(None)]
            ) -> IndexFilter:
        if input_value is None:
            return self.index_filter
        elif isinstance(input_value, IndexFilter):
            return input_value
        else:
            return IndexFilter(max_samples = input_value
                ,random_state= self.random_state)


    def get_X_col_filter(self
                , a_filter:Union[ColumnFilter, List[str], None]
                ) -> Optional[ColumnFilter]:
        if a_filter is None:
            return self.X_col_filter
        elif isinstance(a_filter, ColumnFilter):
            return a_filter
        else:
            return ColumnFilter(a_filter)


    def get_Y_col_filter(self
                , a_filter:Union[ColumnFilter, List[str], None]
                ) -> Optional[ColumnFilter]:
        if a_filter is None:
            return self.Y_col_filter
        elif isinstance(a_filter, ColumnFilter):
            return a_filter
        else:
            return ColumnFilter(a_filter)


    def get_scoring(self
            ,input_scoring:Union[str,Callable[..., float], None]
            )-> Callable[...,float]:
        if input_scoring is None:
            return self.scoring
        else:
            scorer = get_scorer(input_scoring)
            return scorer


    def get_cv_splitting(self
            ,input_cv:Union[int, BaseCrossValidator, AdaptiveSplitter, None]
            ) -> Union[BaseCrossValidator, AdaptiveSplitter]:
        if input_cv is None:
            return self.cv_splitting
        elif isinstance(input_cv, int):
            return AdaptiveKFold(n_splits=input_cv)
        else:
            assert isinstance(input_cv, (BaseCrossValidator, AdaptiveSplitter))
            return input_cv

class Learner(BaseEstimator,LoggableObject):
    """ Abstract base class for estimators, w/ .val_fit() & .fit() methods.

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    def __init__(self
                 , *
                 , defaults:LearnersContext = None
                 , random_state = None
                 , index_filter:Union[int,float,None] = None
                 , X_col_filter:Optional[ColumnFilter] = None
                 , Y_col_filter: Optional[ColumnFilter] = None
                 , root_logger_name: str = None
                 , logging_level: Union[str,int] = "WARNING"):

        if defaults is None:
            defaults = LearnersContext()
        else:
            assert isinstance(defaults, LearnersContext)
        self.defaults = defaults

        root_logger_name = defaults.get_root_logger_name(root_logger_name)
        logging_level = defaults.get_logging_level(logging_level)

        super().__init__(
            root_logger_name = root_logger_name
            ,logging_level=logging_level)

        self.random_state = defaults.get_random_state(random_state)
        self.index_filter = defaults.get_index_filter(index_filter)
        self.X_col_filter = defaults.get_X_col_filter(X_col_filter)
        self.Y_col_filter = defaults.get_Y_col_filter(Y_col_filter)

    def fit(self
            ,X:pd.DataFrame
            ,Y:pd.DataFrame
            ,**kwargs):
        raise NotImplementedError

    def val_fit(self
                ,X:pd.DataFrame
                ,Y:pd.DataFrame
                ,X_val:pd.DataFrame
                ,Y_val:pd.DataFrame
                ,**kwargs):
        raise NotImplementedError

    def _preprocess_params(self):

        if self.defaults is None:
            self.defaults = LearnersContext()

        self.root_logger_name = self.defaults.get_root_logger_name(
            self.root_logger_name)

        self.logging_level = self.defaults.get_logging_level(
            self.logging_level)

        self.update_logger(new_logging_level = self.logging_level)

        self.index_filter = self.defaults.get_index_filter(self.index_filter)
        self.X_col_filter = self.defaults.get_X_col_filter(self.X_col_filter)
        self.Y_col_filter = self.defaults.get_Y_col_filter(self.Y_col_filter)
        self.random_state = self.defaults.get_random_state(self.random_state)


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


    def _get_samples(self,X:pd.DataFrame, Y:Optional[pd.DataFrame]):
        (X_samples, Y_samples) = self.index_filter.filter(X,Y)
        X_samples = self.X_col_filter.filter(X_samples)
        Y_samples = self.Y_col_filter.filter(Y_samples)

        return (X_samples,Y_samples)


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

        (X,Y) = self._get_samples(X,Y)

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
            log_message = f"<== Fitting process has finished."
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

    def input_X_can_have_nans(self) -> Union[bool,NotKnownType]:
        return NotKnown

    def input_Y_can_have_nans(self) -> Union[bool,NotKnownType]:
        return NotKnown


class Mapper(Learner):
    """ Abstract base class for predictors / transformers, implements .map() .

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    def __init__(self
                , *
                , defaults:LearnersContext = None
                , random_state=None
                , index_filter: Union[int, float, None] = None
                , X_col_filter: Optional[ColumnFilter] = None
                , Y_col_filter: Optional[ColumnFilter] = None
                , scoring:Union[str,Callable[..., float], None] = None
                , cv_splitting = None
                , root_logger_name: str = None
                , logging_level = None
                 ) -> None:
        super().__init__(
            defaults = defaults
            ,random_state = random_state
            ,index_filter = index_filter
            ,X_col_filter = X_col_filter
            ,Y_col_filter = Y_col_filter
            ,root_logger_name = root_logger_name
            ,logging_level= logging_level)
        self.scoring = self.defaults.get_scoring(scoring)
        self.cv_splitting = self.defaults.get_cv_splitting(cv_splitting)

    def _preprocess_splitting_param(self):
        self.cv_splitting = self.defaults.get_cv_splitting(self.cv_splitting)

    def _preprocess_scoring_param(self):
        self.scoring = self.defaults.get_scoring(self.scoring)

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
        return self.scoring

    def get_splitter(self) -> BaseCrossValidator:
        self._preprocess_splitting_param()
        return self.cv_splitting

    def get_n_splits(self) -> int:
        self._preprocess_splitting_param()
        return self.cv_splitting.get_n_splits()

    def output_Z_columns(self) -> List[str]:
        return NotKnown

    def output_Z_can_have_nans(self) -> bool:
        return NotKnown

    def output_Z_is_numeric_only(self) -> bool:
        return NotKnown

    def is_leakproof(self) -> bool:
        return False

    def can_detect_overfitting(self) -> bool:
        return NotKnown

    def val_fit(self
                , X:pd.DataFrame
                , Y:pd.DataFrame
                , X_val:pd.DataFrame
                , Y_val:pd.DataFrame
                , **kwargs):

        assert isinstance(self.can_detect_overfitting(), bool) , (
            "Mapper's child class must implement either "
            ".fit("") or .val_fit() method, and its "
            ".can_detect_overfitting() method"
            " must return strictly True or False "
            "(as opposite to NotKnown)")

        if self.can_detect_overfitting():
            raise NotImplementedError(
                "When a Mapper's child IS capable to detect overfitting "
                "during training, it must implement its own version of "
                ".val_fit() method (as opposite to "
                "using default implementation)" )

        log_message = f"{self.__class__.__name__} "
        log_message += f"is not equipped with outfitting detection; "
        log_message += f"{len(X_val)} sampples in validation dataset "
        log_message += f"will be ignored, "
        log_message += f"classic .fit() method will be used "
        log_message += f"instead of .val_fit() ."
        self.warning(log_message)
        self.fit(X,Y, **kwargs)
        return self


    def fit(self
            ,X:pd.DataFrame
            ,Y:pd.DataFrame
            ,**kwargs):

        assert isinstance(self.can_detect_overfitting(), bool), (
            "Mapper's child class must implement either "
            ".fit("") or .val_fit() method, and its "
            ".can_detect_overfitting() method "
            "must return strictly True or False "
            "(as opposite to NotKnown)")

        if not self.can_detect_overfitting():
            raise NotImplementedError(
                "When a Mapper's child is NOT capable to detect overfitting "
                "during training, it must implement its own version of "
                ".fit() method (as opposite to "
                "using default implementation)")

        splitter = self.get_splitter()
        for (train_idx,val_idx) in splitter.split(X, Y):
            X_train = X.iloc[train_idx]
            Y_train = Y.iloc[train_idx]
            X_val = X.iloc[val_idx]
            Y_val = Y.iloc[val_idx]
            break

        self.val_fit(
            X=X_train
            ,Y=Y_train
            ,X_val=X_val
            ,Y_val=Y_val
            ,**kwargs)
        return self
