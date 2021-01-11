import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from numpy import mean, median
from sklearn import clone
from sklearn.base import BaseEstimator
from sklearn.metrics import get_scorer
from sklearn.metrics._scorer import _BaseScorer
from sklearn.model_selection import BaseCrossValidator
from sklearn.base import is_regressor, is_classifier

from Pythagoras.misc_utils import *
from Pythagoras.not_known import *
from Pythagoras.loggers import *
from Pythagoras.caching import *
from Pythagoras.splitters import *
from Pythagoras.filters import *
# from Pythagoras.converters import *


# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
class Learner(LoggableObject, BaseEstimator):
    pass

def dual_scorer(
        regression_scoring:Union[str, Callable] = "r2"
        , classification_scoring:Union[str, Callable] = "balanced_accuracy"):
    regr_scorer = get_scorer(regression_scoring)
    class_scorer = get_scorer(classification_scoring)

    def new_scorer(estimator, X, Y):
        if is_regressor(estimator):
            return regr_scorer(estimator, X, Y)
        elif is_classifier(estimator):
            return class_scorer(estimator, X, Y)
        else:
            raise ValueError("Not supported type of Estimator")

    return new_scorer

class LearningContext:
    root_logger_name:Optional[str]
    logging_level:Union[int,str,type(None)]

    random_state: Any

    index_filer:RowFilter
    x_col_filter:ColumnFilter
    y_col_filter:ColumnFilter

    scoring:Callable[..., float]
    splitting:Union[BaseCrossValidator, AdaptiveSplitter]

    id_in_index:bool

    def __init__(self
                 , *
                 , random_state = None
                 , root_logger_name = None
                 , logging_level = None
                 , row_fittime_filter:Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
                 , x_col_alltime_filter:Union[ColumnFilter, List[str], int, None] = None
                 , y_col_allltime_filter:Union[ColumnFilter, List[str], int, None] = None
                 , scoring:Union[str,Callable[..., float], None] = None
                 , splitting:Union[
                BaseCrossValidator, AdaptiveSplitter, int, None] = None
                 , id_in_index:bool = None
                 ) -> None:
        self.random_state = None
        self.random_state = self.get_random_state(random_state)

        self.root_logger_name = "Pythagoras"
        self.root_logger_name = self.get_root_logger_name(root_logger_name)

        self.logging_level = lg.WARNING
        self.logging_level = self.get_logging_level(logging_level)

        self.row_filter = RowFilter()
        self.row_filter = self.get_row_fittime_filter(row_fittime_filter)

        self.x_col_alltime_filter = ColumnFilter()
        self.x_col_alltime_filter = self.get_x_col_alltime_filter(x_col_alltime_filter)

        self.y_col_alltime_filter = ColumnFilter()
        self.y_col_alltime_filter = self.get_y_col_alltime_filter(x_col_alltime_filter)

        self.scoring = dual_scorer()
        self.scoring = self.get_scoring(scoring)

        self.splitting = AdaptiveKFold(
            n_splits=5
            , random_state = self.random_state
            , root_logger_name = self.root_logger_name
            , logging_level = self.logging_level)
        self.splitting = self.get_splitting(splitting)

        self.id_in_index = False
        self.id_in_index = self.get_id_in_index(id_in_index)


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


    def get_row_fittime_filter(self
            , input_filter:Union[RowFilter, int, float, type(None)]
            ) -> RowFilter:
        if input_filter is None:
            return self.row_filter
        elif isinstance(input_filter, RowFilter):
            return input_filter
        else:
            return RowFilter(max_samples = input_filter
                             , random_state= self.random_state)


    def get_x_col_alltime_filter(self
                                 , a_filter:Union[ColumnFilter,List[str],int,None]
                                 ) -> Optional[ColumnFilter]:
        if a_filter is None:
            return self.x_col_alltime_filter
        elif isinstance(a_filter, ColumnFilter):
            return a_filter
        else:
            return ColumnFilter(a_filter)


    def get_y_col_alltime_filter(self
                                 , a_filter:Union[ColumnFilter,List[str],int,None]
                                 ) -> Optional[ColumnFilter]:
        if a_filter is None:
            return self.y_col_alltime_filter
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


    def get_splitting(self
            , input_splitting:Union[int, BaseCrossValidator, AdaptiveSplitter, None]
            ) -> Union[BaseCrossValidator, AdaptiveSplitter]:
        if input_splitting is None:
            return self.splitting
        elif isinstance(input_splitting, int):
            return AdaptiveKFold(n_splits=input_splitting)
        else:
            assert isinstance(input_splitting, (BaseCrossValidator, AdaptiveSplitter))
            return input_splitting


    def get_id_in_index(self
            ,input_id_in_index:bool
            )-> bool:
        if input_id_in_index is None:
            return self.id_in_index
        else:
            return input_id_in_index


class Learner(BaseEstimator,LoggableObject):
    """ Abstract base class for estimators, w/ .val_fit() & .fit() methods.

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    def __init__(self
                 , *
                 , defaults:LearningContext = None
                 , random_state = None
                 , row_fittime_filter:Union[int, float, None] = None
                 , x_col_alltime_filter:Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , id_in_index:bool = None
                 , root_logger_name: str = None
                 , logging_level: Union[str,int] = "WARNING"):

        if defaults is None:
            defaults = LearningContext()
        else:
            assert isinstance(defaults, LearningContext)
        self.defaults = defaults

        root_logger_name = defaults.get_root_logger_name(root_logger_name)
        logging_level = defaults.get_logging_level(logging_level)

        super().__init__(
            root_logger_name = root_logger_name
            ,logging_level=logging_level)

        self.random_state = defaults.get_random_state(random_state)
        self.row_fittime_filter = defaults.get_row_fittime_filter(row_fittime_filter)
        self.x_col_alltime_filter = defaults.get_x_col_alltime_filter(x_col_alltime_filter)
        self.y_col_alltime_filter = defaults.get_y_col_alltime_filter(y_col_alltime_filter)
        self.id_in_index = defaults.get_id_in_index(id_in_index)

    def log_id(self) -> str:
        a_name = self.__class__.__name__
        return a_name

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
            self.defaults = LearningContext()

        self.root_logger_name = self.defaults.get_root_logger_name(
            self.root_logger_name)

        self.logging_level = self.defaults.get_logging_level(
            self.logging_level)

        self.update_logger(new_logging_level = self.logging_level)

        self.row_fittime_filter = self.defaults.get_row_fittime_filter(self.row_fittime_filter)
        self.x_col_alltime_filter = self.defaults.get_x_col_alltime_filter(self.x_col_alltime_filter)
        self.y_col_alltime_filter = self.defaults.get_y_col_alltime_filter(self.y_col_alltime_filter)
        self.random_state = self.defaults.get_random_state(self.random_state)
        self.id_in_index = self.defaults.get_id_in_index(self.id_in_index)


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


    def _fittime_filter(self, X:pd.DataFrame, Y:Optional[pd.DataFrame]):
        (X_result, Y_result) = self.row_fittime_filter.filter(X, Y)
        X_result = self.x_col_alltime_filter.filter(X_result)
        if Y is not None:
            Y_result = self.y_col_alltime_filter.filter(Y_result)

        return (X_result,Y_result)

    def _maptime_filter(self, X: pd.DataFrame):
        X_result = self.x_col_alltime_filter.filter(X)
        return X_result

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

        (X,Y) = self._fittime_filter(X, Y)

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

def get_log_id(an_object) -> str:
    try:
        a_name =  an_object.log_id()
    except:
        a_name = an_object.__class__.__name__
    return a_name

class Mapper(Learner):
    """ Abstract base class for predictors / transformers, implements .map() .

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    def __init__(self
                 , *
                 , defaults:LearningContext = None
                 , random_state=None
                 , row_fittime_filter: Union[int, float, None] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , scoring:Union[str,Callable[..., float], None] = None
                 , splitting = None
                 , root_logger_name: str = None
                 , logging_level = None
                 ) -> None:
        super().__init__(
            defaults = defaults
            ,random_state = random_state
            , row_fittime_filter= row_fittime_filter
            , x_col_alltime_filter= x_col_alltime_filter
            , y_col_alltime_filter= y_col_alltime_filter
            ,root_logger_name = root_logger_name
            ,logging_level= logging_level)
        self.scoring = self.defaults.get_scoring(scoring)
        self.splitting = self.defaults.get_splitting(splitting)

    def _preprocess_splitting_param(self):
        self.splitting = self.defaults.get_splitting(self.splitting)

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
        self.pre_mapping_x_idx_ = deepcopy(X.index)

        if self.input_X_columns() is NotKnown:
            pass
        else:
            assert set(self.input_X_columns()) <= set(X)
            X = deepcopy(X[self.input_X_columns()])

        X = self._maptime_filter(X)

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
        assert len(Z) == len(self.pre_mapping_x_idx_)
        assert set(Z.index) == set(self.pre_mapping_x_idx_)

        if self.output_Z_can_have_nans() is NotKnown:
            pass
        elif not self.output_Z_can_have_nans():
            assert n_nans == 0

        if self.output_Z_columns() is not NotKnown:
            assert set(Z.columns) == set(self.output_Z_columns())

        Z = Z.reindex(index=self.pre_mapping_x_idx_) # TODO: Check whether it works as intended

        return Z


    def predict(self,X:pd.DataFrame)->pd.DataFrame:
        if is_regressor(self):
            predictions =  self.map(X)
        elif is_classifier(self):
            probabilities = self.map(X)
            predictions = probabilities.to_numpy().argmax(axis=1)
        else:
            error_msg = "Predictions can only be generated "
            error_msg += "by regressors or classifiers."
            raise Exception(error_msg)

        return predictions

    def predict_proba(self,X:pd.DataFrame)->pd.DataFrame:
        if is_classifier(self):
            probabilities = self.map(X)
        else:
            error_msg = "Probabilities can only be generated "
            error_msg += "by classifiers."
            raise Exception(error_msg)

        # conversion to numpy is
        # a dirty trick to make SKLearn _ProbaScorer work
        # TODO: refactor

        return probabilities #.to_numpy()

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.map(X)

    def get_scorer(self) -> _BaseScorer:
        self._preprocess_scoring_param()
        return self.scoring

    def get_splitter(self) -> BaseCrossValidator:
        self._preprocess_splitting_param()
        return self.splitting

    def get_n_splits(self) -> int:
        self._preprocess_splitting_param()
        return self.splitting.get_n_splits()

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

        self._start_val_fitting(X,Y,X_val,Y_val, write_to_log=False)

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
