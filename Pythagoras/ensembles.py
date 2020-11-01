import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from numpy import mean, median
from sklearn import clone
from sklearn.base import BaseEstimator
from sklearn.metrics import get_scorer
from sklearn.metrics._scorer import _BaseScorer
from sklearn.model_selection import cross_val_score, RepeatedKFold, KFold, \
    StratifiedKFold, BaseCrossValidator

from Pythagoras.misc_utils import *
from Pythagoras.not_known import *
from Pythagoras.logging import *
from Pythagoras.caching import *
from Pythagoras.base import *

class SimpleMetaMapper(Mapper):
    def __init__(self
                 , *
                 , defaults: LearningContext = None
                 , base_mapper:Mapper
                 , cv_splitting = 5
                 , scoring = "r2"
                 , index_filter: Union[int, float, type(None)] = None
                 , X_col_filter: Optional[ColumnFilter] = None
                 , Y_col_filter: Optional[ColumnFilter] = None
                 , random_state = None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level = logging.WARNING):
        super().__init__(
            defaults = defaults
            , index_filter = index_filter
            , X_col_filter=X_col_filter
            , Y_col_filter=Y_col_filter
            , random_state = random_state
            , cv_splitting = cv_splitting
            , scoring = scoring
            , root_logger_name = root_logger_name
            , logging_level= logging_level )
        self.base_mapper = base_mapper
        if hasattr(self.base_mapper, "_estimator_type"):
            self._estimator_type = self.base_mapper._estimator_type

    def input_X_can_have_nans(self) -> bool:
        return self.base_mapper.input_X_can_have_nans()

    def input_Y_can_have_nans(self) -> bool:
        return self.base_mapper.input_Y_can_have_nans()

    def typeid(self) -> str:
        a_name = super().typeid()
        a_name += f"< {get_typeid(self.base_mapper)} >"
        return a_name


class KFoldEnsemble(SimpleMetaMapper):
    """ Generic KFold Ensembler
    """

    def __init__(self
                 , *
                 , base_mapper:Mapper
                 , defaults: LearningContext = None
                 , fit_strategy = "fit"
                 , cv_splitting = None
                 , scoring = None
                 , n_mappers_in_ensemble:Union[int, float, type(None)] = 0.55
                 , full_model_weight:Optional[int] = 1
                 , index_filter: Union[int,float,None] = None
                 , X_col_filter: Union[ColumnFilter,List[str],int,None] = None
                 , Y_col_filter: Union[ColumnFilter,List[str],int,None] = None
                 , random_state = None
                 , root_logger_name: str = None
                 , logging_level = None
                 ) -> None:
        super().__init__(
            base_mapper = base_mapper
            , defaults = defaults
            , index_filter = index_filter
            , X_col_filter = X_col_filter
            , Y_col_filter = Y_col_filter
            , random_state = random_state
            , cv_splitting = cv_splitting
            , scoring = scoring
            , root_logger_name = root_logger_name
            , logging_level= logging_level )
        self.fit_strategy = fit_strategy
        self.n_mappers_in_ensemble = n_mappers_in_ensemble
        self.full_model_weight = full_model_weight

    def _preprocess_params(self):
        super()._preprocess_params()

        if self.fit_strategy is None:
            self.fit_strategy = "fit"
        assert self.fit_strategy in {"fit","val_fit"}

        if (not self.base_mapper.can_detect_overfitting()
            and self.fit_strategy == "val_fit"):
            log_message = "Inefficient combination of parameters."
            self.warning(log_message)

        assert isinstance(self.n_mappers_in_ensemble, (int, float, type(None)))
        self._n_mappers = self.n_mappers_in_ensemble
        if self._n_mappers is None:
            self._n_mappers = self.get_n_splits()
        elif isinstance(self._n_mappers, float):
            assert 0.0 <= self._n_mappers <= 1.0
            self._n_mappers = int(self.get_n_splits()*self._n_mappers)
            self._n_mappers = min(self.get_n_splits(), self._n_mappers)
            self._n_mappers = max(0, self._n_mappers)
        elif self._n_mappers <0 and isinstance(self._n_mappers, int):
            self._n_mappers += self.get_n_splits()
        assert 0 <= self._n_mappers <= self.get_n_splits(), (
            f"n_mappers_in_ensemble={self.n_mappers_in_ensemble}"
            f", _n_mappers={self._n_mappers}"
            f", get_n_splits()={self.get_n_splits()}")

        if self.full_model_weight is None:
            self.full_model_weight = 0
        assert self.full_model_weight >= 0

    def is_leakproof(self) -> bool:
        self._preprocess_params()
        if self.fit_strategy == "fit":
            return True
        else:
            return False

    def can_detect_overfitting(self) -> bool:
        return False

    def fit(self,X,Y,**kwargs):

        (X,Y) = self._start_fitting(X, Y)
        self.kfold_mappers_ = []

        spltr = self.get_splitter()

        for train_idx, val_idx in spltr.split(X,Y):
            X_train = X.iloc[train_idx]
            Y_train = Y.iloc[train_idx]
            X_val = X.iloc[val_idx]
            Y_val = Y.iloc[val_idx]

            new_mapper = self._build_new_mapper(
                X_train, Y_train, X_val, Y_val, **kwargs)

            self.kfold_mappers_ += [new_mapper]

        if self.full_model_weight != 0:
            self.full_mapper = clone(self.base_mapper)
            self.full_mapper.fit(X,Y, **kwargs)

        self.kfold_mappers_ = sorted(
            self.kfold_mappers_
            , key = lambda m:m.cv_score_
            , reverse=True)

        self._finish_fitting()

        return self

    def _map_training_X(self, X:pd.DataFrame, **kwargs) -> pd.DataFrame:
        log_message = f"Executing KFold mapping process for {len(X)} samples"
        log_message += f" that were previously present in the train set."
        self.debug(log_message)

        fold_results = []
        for fm in self.kfold_mappers_:
            X_fm = X[X.index.isin(fm.val_fit_idset_)]
            if len(X_fm)==0:
                continue
            new_result = fm.map(X_fm,**kwargs)
            fold_results += [new_result]
        Z = pd.concat(fold_results, axis="index")
        assert set(Z.index) == set(X.index)
        return Z

    def _map_testing_X(self, X:pd.DataFrame,**kwargs) -> pd.DataFrame:
        assert self._n_mappers or self.full_model_weight

        log_message = "Executing direct mapping process for "
        log_message +=f"{len(X)} samples that were not seen before."
        self.debug(log_message)

        fold_results = []

        for fm in self.kfold_mappers_[:self._n_mappers]:
            fold_results += [fm.map(X,**kwargs)]

        if len(fold_results):
            Z = sum(fold_results) # TODO: check
            if self.full_model_weight !=0:
                Z += self.full_mapper.map(X,**kwargs)*self.full_model_weight
            Z /= len(fold_results) + self.full_model_weight
        else:
            Z = self.full_mapper.map(X,**kwargs)

        assert set(Z.index) == set(X.index)

        return Z

    def map(self, X: pd.DataFrame,**kwargs) -> pd.DataFrame:
        assert self.base_mapper.output_Z_is_numeric_only()
        X = self._start_mapping(X)
        X_training_idx = X.index.isin(self.full_fit_idset_)
        X_train = X[X_training_idx]
        X_test = X[~(X_training_idx)]
        all_Z = []
        if len(X_train):
            Z_train = self._map_training_X(X_train,**kwargs)
            all_Z += [Z_train]
        if len(X_test):
            Z_test = self._map_testing_X(X_test,**kwargs)
            all_Z += [Z_test]
        Z = pd.concat(all_Z, axis="index")
        Z = self._finish_mapping(Z)
        return Z

    def _build_new_mapper(self, X, Y, X_val, Y_val, **kwargs):
        new_mapper = clone(self.base_mapper)
        if self.fit_strategy == "fit":
            new_mapper.fit(X,Y,**kwargs)
            new_mapper.val_fit_idset_ = set(X_val.index)
        elif self.fit_strategy == "val_fit":
            new_mapper.fit_val(X, Y, X_val, Y_val,**kwargs)
        new_mapper.cv_score_ = self.get_scorer()(new_mapper,X_val,Y_val)
        return new_mapper


class LeakProofMapper(KFoldEnsemble):
    """ LeakProof Mapper
    """

    def __init__(self
            , *
            , base_mapper: Mapper
            , cv_splitting=None
            , scoring=None
            , index_filter: Union[int, float, None] = None
            , X_col_filter: Union[ColumnFilter, List[str], int, None] = None
            , Y_col_filter: Union[ColumnFilter, List[str], int, None] = None
            , random_state=None
            , root_logger_name: str = "Pythagoras"
            , logging_level=logging.WARNING
            ) -> None:
        super().__init__(
            fit_strategy = "fit"
            , n_mappers_in_ensemble= 0
            , full_model_weight = 1
            , base_mapper = base_mapper
            , cv_splitting = cv_splitting
            , scoring = scoring
            , index_filter = index_filter
            , X_col_filter = X_col_filter
            , Y_col_filter = Y_col_filter
            , random_state=random_state
            , root_logger_name=root_logger_name
            , logging_level=logging_level)
