import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict
import logging as lg

from catboost import CatBoostRegressor, CatBoostClassifier, CatBoost
from lightgbm import LGBMRegressor, LGBMClassifier
from sklearn.base import is_regressor, is_classifier
from sklearn.datasets import load_iris
from sklearn.linear_model import LinearRegression, LogisticRegression

from Pythagoras.misc_utils import *
from Pythagoras.base import *
from Pythagoras.not_known import *
from Pythagoras.loggers import *
from Pythagoras.caching import *
from Pythagoras.ensembles import *


class EstimatorFromMapper(SimpleMetaMapper):
    def __init__(self
                 , *
                 , defaults: LearningContext = None
                 , base_mapper:Mapper
                 , splitting = None
                 , scoring = None
                 , row_fittime_filter: Union[int, float, type(None)] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , random_state = None
                 , root_logger_name: str = None
                 , logging_level = None
                 ) -> None:
        super().__init__(
            defaults=defaults
            , row_fittime_filter=row_fittime_filter
            , x_col_alltime_filter=x_col_alltime_filter
            , y_col_alltime_filter=y_col_alltime_filter
            , random_state=random_state
            , splitting=splitting
            , scoring=scoring
            , root_logger_name=root_logger_name
            , logging_level=logging_level
            , base_mapper = base_mapper)

    def predict(self,X:pd.DataFrame):
        predictions_df = self.base_mapper.predict(X)
        predictions_np = predictions_df.to_numpy()
        return predictions_np

    def predict_proba(self,X:pd.DataFrame):
        probabilities_df = self.base_mapper.predict_proba(X)
        probabilities_np = probabilities_df.to_numpy()
        return probabilities_np


def upgrade_scorer(skl_scorer:Callable):
    def p_scorer(mapper:Mapper
                   , X:pd.DataFrame
                   , Y:pd.DataFrame):
        if isinstance(mapper, Mapper):
            estimator = EstimatorFromMapper(base_mapper=mapper)
        else:
            estimator = mapper
            assert isinstance(estimator, BaseEstimator)

        return skl_scorer(estimator,X, Y)

    return p_scorer

class MapperFromEstimator(Mapper):
    """A wrapper for SKLearn-compatible estimators
    """

    def __init__(self
                 , base_estimator:BaseEstimator = None
                 , defaults:LearningContext = None
                 , scoring = None
                 , splitting = 5
                 , row_fittime_filter: Union[BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , random_state = None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level = lg.WARNING) -> None:

        super().__init__(
            defaults = defaults
            , scoring=scoring
            , splitting= splitting
            , row_fittime_filter= row_fittime_filter
            , x_col_alltime_filter= x_col_alltime_filter
            , y_col_alltime_filter= y_col_alltime_filter
            , random_state = random_state
            , root_logger_name = root_logger_name
            , logging_level=logging_level)

        self.base_estimator = base_estimator
        self._estimator_type = base_estimator._estimator_type

        if not (isinstance(base_estimator, BaseEstimator)
                or isinstance(base_estimator, CatBoost)):
            log_message = f"base_regressor has type={type(base_estimator)}, "
            log_message += f"which is not inherited "
            log_message += f"from BaseEstimator or CatBoost."
            self.warning(log_message)

        if isinstance(base_estimator, Mapper):
            log_message = f"base_regressor has type={type(base_estimator)}, "
            log_message += f"which is already inherited from Mapper."
            self.warning(log_message)

    def log_id(self) -> str:
        a_name = super().log_id()
        a_name += f"<{get_log_id(self.base_estimator)}>"
        return a_name


    def _preprocess_params(self):
        super()._preprocess_params()
        assert hasattr(self.base_estimator, "fit")
        assert hasattr(self.base_estimator, "predict")
        self.base_estimator = clone(self.base_estimator)

    def score(self,X,Y,**kwargs) -> float:
        assert self.is_fitted()
        scorer = self.get_scorer()
        result = scorer(self.base_estimator,X,Y,**kwargs)
        return result

    def _get_tags(self):
        return self.base_estimator._get_tags()

    def get_feature_importances_df(self):
        assert self.is_fitted()

        if not hasattr(self.base_estimator, "feature_importances_"):
            return NotKnown

        feature_importances = self.base_estimator.feature_importances_

        if hasattr(self.base_estimator, "feature_importances_"):
            feature_names = self.base_estimator.feature_names_
        else:
            feature_names = self.base_estimator.feature_name_

        result_df = pd.DataFrame(
            data=feature_importances
            , index=feature_names
            , columns=["Importance"])
        result_df.index.name = "Feature"
        result_df.sort_values(by="Importance", ascending=False, inplace=True)

        return result_df

class MapperFromRegressor(MapperFromEstimator):
    """A wrapper for SKLearn-compatible regressors
    """

    def __init__(self
                 , base_estimator:BaseEstimator = None
                 , defaults:LearningContext = None
                 , scoring = None
                 , splitting = 5
                 , row_fittime_filter: Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , random_state = None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level = lg.WARNING) -> None:

        super().__init__(
            base_estimator=base_estimator
            , defaults = defaults
            , scoring=scoring
            , splitting= splitting
            , row_fittime_filter= row_fittime_filter
            , x_col_alltime_filter= x_col_alltime_filter
            , y_col_alltime_filter= y_col_alltime_filter
            , random_state = random_state
            , root_logger_name = root_logger_name
            , logging_level=logging_level)


    def _preprocess_params(self):
        super()._preprocess_params()
        assert is_regressor(self.base_estimator)

    def map(self,X:pd.DataFrame) -> pd.DataFrame:
        X = self._start_mapping(X)
        Z = self.base_estimator.predict(X)
        Z = pd.DataFrame(data=Z, index=X.index, columns=self.Y_column_names_)
        Z = self._finish_mapping(Z)
        return Z


class MapperFromSKLNRegressor(MapperFromRegressor):
    """A wrapper for SKLearn regressors
    """

    def __init__(self
                 , base_estimator:BaseEstimator = None
                 , defaults:LearningContext = None
                 , scoring = None
                 , splitting = 5
                 , row_fittime_filter: Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , random_state = None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level = lg.WARNING) -> None:

        if base_estimator is None:
            base_estimator = LinearRegression()

        super().__init__(
            defaults = defaults
            , base_estimator= base_estimator
            , scoring=scoring
            , splitting= splitting
            , row_fittime_filter= row_fittime_filter
            , x_col_alltime_filter= x_col_alltime_filter
            , y_col_alltime_filter= y_col_alltime_filter
            , random_state = random_state
            , root_logger_name = root_logger_name
            , logging_level=logging_level)


    def fit(self,X:pd.DataFrame,Y:pd.DataFrame,**kwargs):
        (X,Y) = self._start_fitting(X, Y)
        self.base_estimator.fit(X, Y, **kwargs)
        self._finish_fitting()
        return self

    def can_detect_overfitting(self) -> bool:
        return False


class MapperFromLGBMRegressor(MapperFromRegressor):
    """A wrapper for LightGBM regressor
    """

    def __init__(self
                 , base_estimator:LGBMRegressor = None
                 , defaults:LearningContext = None
                 , scoring = None
                 , splitting = 5
                 , row_fittime_filter: Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , random_state = None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level = None) -> None:


        if base_estimator is None:
            base_estimator = LGBMRegressor(random_state=random_state)

        super().__init__(
            defaults = defaults
            , base_estimator= base_estimator
            , scoring=scoring
            , splitting= splitting
            , row_fittime_filter= row_fittime_filter
            , x_col_alltime_filter= x_col_alltime_filter
            , y_col_alltime_filter= y_col_alltime_filter
            , random_state = random_state
            , root_logger_name = root_logger_name
            , logging_level=logging_level)

    def _preprocess_params(self):
        super()._preprocess_params()
        assert isinstance(self.base_estimator, LGBMRegressor)


    def val_fit(self, X, Y, X_val, Y_val, **kwargs):
        X, y, X_val, y_val = self._start_val_fitting(X, Y, X_val, Y_val)
        if not "verbose" in kwargs:
            kwargs["verbose"]=False
        self.base_estimator.fit(X, Y, eval_set=(X_val, y_val), **kwargs)
        self._finish_fitting()
        return self

    def can_detect_overfitting(self) -> bool:
        return True


class MapperFromCATBOOSTRegressor(MapperFromRegressor):
    """A wrapper for SKLearn regressors
    """

    def __init__(self
                 , base_estimator:CatBoostRegressor=None
                 , defaults: LearningContext = None
                 , scoring=None
                 , splitting=5
                 , row_fittime_filter: Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , random_state=None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level=lg.WARNING) -> None:

        if base_estimator is None:
            base_estimator = CatBoostRegressor(random_state=random_state)

        super().__init__(
            defaults=defaults
            , base_estimator=base_estimator
            , scoring=scoring
            , splitting=splitting
            , row_fittime_filter=row_fittime_filter
            , x_col_alltime_filter=x_col_alltime_filter
            , y_col_alltime_filter=y_col_alltime_filter
            , random_state=random_state
            , root_logger_name=root_logger_name
            , logging_level=logging_level)

    def _preprocess_params(self):
        super()._preprocess_params()
        assert isinstance(self.base_estimator, CatBoostRegressor)

    def val_fit(self, X, Y, X_val, Y_val, **kwargs):
        X, Y, X_val, Y_val = self._start_val_fitting(X, Y, X_val, Y_val)
        X_cat_names = list(X.dtypes[X.dtypes == "category"].index)
        X_val_cat_names = list(X_val.dtypes[X_val.dtypes == "category"].index)
        assert set(X_cat_names) == set(X_val_cat_names)
        if not "verbose" in kwargs:
            kwargs["verbose"]=False
        self.base_estimator.fit(X
                                , Y
                                , eval_set=(X_val, Y_val)
                                , cat_features=X_cat_names
                                , **kwargs)

        self._finish_fitting()
        return self

    def can_detect_overfitting(self) -> bool:
        return True


class MapperFromClassifier(MapperFromEstimator):
    """A wrapper for SKLearn-compatible classifier
    """

    def __init__(self
                 , base_estimator:BaseEstimator = None
                 , defaults:LearningContext = None
                 , scoring = None
                 , splitting = 5
                 , row_fittime_filter: Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , random_state = None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level = None) -> None:

        super().__init__(
            base_estimator=base_estimator
            , defaults = defaults
            , scoring=scoring
            , splitting= splitting
            , row_fittime_filter= row_fittime_filter
            , x_col_alltime_filter= x_col_alltime_filter
            , y_col_alltime_filter= y_col_alltime_filter
            , random_state = random_state
            , root_logger_name = root_logger_name
            , logging_level=logging_level)


    def _preprocess_params(self):
        super()._preprocess_params()
        assert is_classifier(self.base_estimator)


    def map(self,X:pd.DataFrame) -> pd.DataFrame:
        Z = self.predict_proba(X)
        return Z


    def predict_proba(self,X:pd.DataFrame) -> pd.DataFrame:
        assert hasattr(self.base_estimator, "predict_proba")
        X = self._start_mapping(X)
        Z = self.base_estimator.predict_proba(X)
        Z = pd.DataFrame(
            data=Z
            , index=X.index
            , columns=[f"P({c})" for c in self.base_estimator.classes_])
        Z = self._finish_mapping(Z)
        # conversion to numpy is
        # a dirty trick to make SKLearn _ProbaScorer work
        # TODO: refactor
        return Z #.to_numpy()


    def predict(self,X:pd.DataFrame) ->pd.DataFrame:
        X = self._start_mapping(X)
        P = self.base_estimator.predict(X)
        P = pd.DataFrame(data=P,index=X.index, columns=self.Y_column_names_)
        P = self._finish_mapping(P)
        return P


class MapperFromSKLNClassifier(MapperFromClassifier):
    """A wrapper for SKLearn regressors
    """

    def __init__(self
                 , base_estimator:BaseEstimator = None
                 , defaults:LearningContext = None
                 , scoring = None
                 , splitting = 5
                 , row_fittime_filter: Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , random_state = None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level = None) -> None:

        if base_estimator is None:
            base_estimator = LogisticRegression(random_state=random_state)

        super().__init__(
            defaults = defaults
            , base_estimator= base_estimator
            , scoring=scoring
            , splitting= splitting
            , row_fittime_filter= row_fittime_filter
            , x_col_alltime_filter= x_col_alltime_filter
            , y_col_alltime_filter= y_col_alltime_filter
            , random_state = random_state
            , root_logger_name = root_logger_name
            , logging_level=logging_level)


    def fit(self,X:pd.DataFrame,Y:pd.DataFrame,**kwargs):
        (X,Y) = self._start_fitting(X, Y)
        self.base_estimator.fit(X, Y, **kwargs)
        self._finish_fitting()
        return self

    def can_detect_overfitting(self) -> bool:
        return False


class MapperFromCATBOOSTClassifier(MapperFromClassifier):
    """A wrapper for SKLearn regressors
    """

    def __init__(self
                 , base_estimator:CatBoostClassifier = None
                 , defaults:LearningContext = None
                 , scoring = None
                 , splitting = 5
                 , row_fittime_filter: Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , random_state = None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level = None) -> None:

        if base_estimator is None:
            base_estimator = CatBoostClassifier(random_state=random_state)

        super().__init__(
            defaults = defaults
            , base_estimator= base_estimator
            , scoring=scoring
            , splitting= splitting
            , row_fittime_filter= row_fittime_filter
            , x_col_alltime_filter= x_col_alltime_filter
            , y_col_alltime_filter= y_col_alltime_filter
            , random_state = random_state
            , root_logger_name = root_logger_name
            , logging_level=logging_level)


    def _preprocess_params(self):
        super()._preprocess_params()
        assert isinstance(self.base_estimator, CatBoostClassifier)


    def val_fit(self, X, Y, X_val, Y_val, **kwargs):
        X, Y, X_val, Y_val = self._start_val_fitting(X, Y, X_val, Y_val)
        X_cat_names = list(X.dtypes[X.dtypes == "category"].index)
        X_val_cat_names = list(X_val.dtypes[X_val.dtypes == "category"].index)
        assert set(X_cat_names) == set(X_val_cat_names)
        if not "verbose" in kwargs:
            kwargs["verbose"]=False
        self.base_estimator.fit(X
                                , Y
                                , eval_set=(X_val, Y_val)
                                , cat_features=X_cat_names
                                , **kwargs)

        self._finish_fitting()
        return self

    def can_detect_overfitting(self) -> bool:
        return True


class MapperFromLGBMClassifier(MapperFromClassifier):
    """A wrapper for SKLearn regressors
    """

    def __init__(self
                 , base_estimator:LGBMClassifier = None
                 , defaults:LearningContext = None
                 , scoring = None
                 , splitting = 5
                 , row_fittime_filter: Union[
                BaseCrossValidator, AdaptiveSplitter, int, float, None] = None
                 , x_col_alltime_filter: Optional[ColumnFilter] = None
                 , y_col_alltime_filter: Optional[ColumnFilter] = None
                 , random_state = None
                 , root_logger_name: str = "Pythagoras"
                 , logging_level = None) -> None:

        if base_estimator is None:
            base_estimator = LGBMClassifier(random_state=random_state)

        super().__init__(
            defaults = defaults
            , base_estimator= base_estimator
            , scoring=scoring
            , splitting= splitting
            , row_fittime_filter= row_fittime_filter
            , x_col_alltime_filter= x_col_alltime_filter
            , y_col_alltime_filter= y_col_alltime_filter
            , random_state = random_state
            , root_logger_name = root_logger_name
            , logging_level=logging_level)

    def _preprocess_params(self):
        super()._preprocess_params()
        assert isinstance(self.base_estimator, LGBMClassifier)

    def val_fit(self, X, Y, X_val, Y_val, **kwargs):
        X, y, X_val, y_val = self._start_val_fitting(X, Y, X_val, Y_val)
        if not "verbose" in kwargs:
            kwargs["verbose"] = False
        self.base_estimator.fit(X, Y, eval_set=(X_val, y_val), **kwargs)
        self._finish_fitting()
        return self

    def can_detect_overfitting(self) -> bool:
        return True


def get_mapper(estimator:Union[BaseEstimator,str], leakproof = False, **kwargs) -> Mapper:

    if isinstance(estimator,str):
        estimator = estimator.lower()

    if isinstance(estimator, Mapper):
        mapper = estimator ## ?!?!?!?
    elif isinstance(estimator, CatBoostRegressor):
        mapper = MapperFromCATBOOSTRegressor(base_estimator=estimator, **kwargs)
    elif estimator == "catboostregressor":
        mapper = MapperFromCATBOOSTRegressor(**kwargs)
    elif isinstance(estimator, LGBMRegressor):
        mapper =  MapperFromLGBMRegressor(base_estimator=estimator, **kwargs)
    elif estimator == "lgbmregressor":
        mapper = MapperFromLGBMRegressor(**kwargs)
    elif is_regressor(estimator):
        mapper =  MapperFromSKLNRegressor(base_estimator=estimator, **kwargs)

    elif isinstance(estimator, CatBoostClassifier):
        mapper =  MapperFromCATBOOSTClassifier(base_estimator=estimator, **kwargs)
    elif estimator == "catboostclassifier":
        mapper = MapperFromCATBOOSTClassifier(**kwargs)
    elif isinstance(estimator, LGBMClassifier):
        mapper =  MapperFromLGBMClassifier(base_estimator=estimator, **kwargs)
    elif estimator == "lgbmclassifier":
        mapper = LGBMClassifier(**kwargs)
    elif is_classifier(estimator):
        mapper =  MapperFromSKLNClassifier(base_estimator=estimator, **kwargs)

    else:
        error_message = f"An Estimator has type {type(estimator)}, "
        error_message += f"which currently can't be automatically "
        error_message += f"converted into a Mapper."
        raise NotImplementedError(error_message)

    if leakproof == True and not mapper.is_leakproof():
        mapper = LeakProofMapper(base_mapper = mapper)
    else:
        assert leakproof == False

    return mapper