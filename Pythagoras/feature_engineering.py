import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from numpy import mean, median
from sklearn import clone
from sklearn.model_selection import cross_val_score, RepeatedKFold

from Pythagoras.util import *
from Pythagoras.logging import *
from Pythagoras.caching import *

# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
# class PEstimator(LoggableObject):
#     pass

class PEstimator(LoggableObject):
    pass

class PEstimator(LoggableObject):

    def __init__(self, *args, **kwargs):
        kwargs["reveal_calling_method"] = kwargs.get(
            "reveal_calling_method", True)
        super().__init__(*args, **kwargs)


    def get_params(self, deep=True):
        if type(self) == PEstimator:
            raise NotImplementedError
        return dict()


    def set_params(self, **params) -> PEstimator:
        if type(self) == PEstimator:
            raise NotImplementedError
        return self


    def _fix_X(self,X:pd.DataFrame) -> pd.DataFrame:

        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(data=X, copy=True)
            X.columns = ["col_" + str(c) for c in X.columns]
        else:
            X = deepcopy(X)

        return X

    def _fix_y(self,y:pd.Series) -> pd.Series:
        if isinstance(y, pd.Series):
            y = deepcopy(y)
        else:
            y = pd.Series(y, copy=True)

        if y.name is None:
            y.name = "y_target"

        return y


    def start_fitting(self
            ,X:Any
            ,y:Any
            ,write_to_log:bool=True
            ) -> Tuple[pd.DataFrame,pd.Series]:

        if write_to_log:
            log_message = f"==> Starting fittig {type(self).__name__} "
            log_message += f"using a {type(X).__name__} named < "
            log_message += NeatStr.object_names(X, div_ch=" / ")
            log_message += f" > with the shape {X.shape}, "
            log_message += f"and a {type(y).__name__} named < "
            log_message += NeatStr.object_names(y, div_ch=" / ") + " >."
            self.info(log_message)

        X = self._fix_X(X)

        if y is not None:
            y = self._fix_y(y)
            assert len(X) == len(y), "X and y must have equal length."

        assert len(X), "X can not be empty."
        assert len(X.columns) == len(set(X.columns)), (
            "Input columns must have unique names.")

        if not self.input_can_have_nans:
            assert X.isna().sum().sum() == 0, "NaN-s are not allowed."

        X.sort_index(inplace=True)

        if y is not None:
            y.sort_index(inplace=True)
            assert set(X.index) == set(y.index)

        X.columns = list(X.columns)

        return (X,y)

    @property
    def is_fitted_(self) -> bool:
        raise NotImplementedError


    @property
    def input_columns_(self) -> List[str]:
        raise NotImplementedError


    @property
    def input_can_have_nans(self) -> bool:
        raise NotImplementedError


    @property
    def output_can_have_nans(self) -> bool:
        raise NotImplementedError



class PFeatureMaker(PEstimator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def output_columns_(self) -> List[str]:
        raise NotImplementedError

    def start_transforming(self
                           , X: pd.DataFrame
                           , write_to_log: bool = True
                           ) -> pd.DataFrame:

        assert self.is_fitted_
        assert len(X)

        if write_to_log:
            log_message = f"==> Starting generating features "
            log_message += f"using a {type(X).__name__} named < "
            log_message += NeatStr.object_names(X, div_ch=" / ")
            log_message += f" > with the shape {X.shape}."
            self.info(log_message)

        X = self._fix_X(X)
        assert set(self.input_columns_) <= set(X)
        X = deepcopy(X[self.input_columns_])

        if not self.input_can_have_nans:
            assert X.isna().sum().sum() == 0

        return X

    def finish_transforming(self
                            , X: pd.DataFrame
                            , write_to_log: bool = True
                            ) -> pd.DataFrame:

        assert len(X)
        assert len(set(X.columns)) == len(X.columns)
        assert set(X.columns) == set(self.output_columns_)

        if write_to_log:
            log_message = f"<== {len(X.columns)} features "
            log_message += "have been generated/returned."
            self.info(log_message)

        if not self.output_can_have_nans:
            assert X.isna().sum().sum() == 0

        return X

    def fit_transform(self
            ,X:pd.DataFrame
            ,y:Optional[pd.Series]=None
            ) -> pd.DataFrame:
        raise NotImplementedError


class NaN_Inducer(PFeatureMaker):
    """A transformer that adds random NaN-s to a dataset"""

    log_df_: Optional[pd.DataFrame]
    transformabe_columns_: Optional[List[str]]
    min_nan_level: float

    def __init__(self, min_nan_level: float = 0.05, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_params(min_nan_level)

    def get_params(self, deep=True):
        params = {"min_nan_level": self.min_nan_level}
        return params

    def set_params(self
                   , min_nan_level
                   ):
        assert 0 <= min_nan_level < 1
        self.min_nan_level = min_nan_level
        self.transformabe_columns_ = None
        self.log_df_ = None
        return self

    @property
    def is_fitted_(self) -> bool:
        return self.transformabe_columns_ is not None

    @property
    def input_can_have_nans(self) -> bool:
        return True

    @property
    def output_can_have_nans(self) -> bool:
        return True

    @property
    def input_columns_(self) -> List[str]:
        assert self.is_fitted_
        return sorted(self.transformabe_columns_)

    @property
    def output_columns_(self) -> List[str]:
        return self.input_columns_

    def fit_transform(self
                      , X: pd.DataFrame
                      , y: Optional[pd.Series] = None
                      ) -> pd.DataFrame:

        type_of_x = type(X).__name__
        self.log_df_ = pd.DataFrame()
        (X, y) = self.start_fitting(X, y, write_to_log=False)
        assert isinstance(X, pd.DataFrame)
        total_nans = int(X.isna().sum().sum())
        total_values = X.shape[0] * X.shape[1]
        current_nan_level = total_nans / total_values
        log_message = f"==> Starting adding random NaNs "
        log_message += f"to a copy of a {type_of_x} "
        log_message += "named < " + NeatStr.object_names(X, div_ch=" / ")
        log_message += f" > with shape {X.shape}, aiming to reach "
        log_message += f"{self.min_nan_level:.2%} level for each column. "
        log_message += f"Currently the dataset contains {total_nans} NaN-s,"
        log_message += f" which is {current_nan_level:.2%}"
        log_message += f" of {total_values} values from the dataframe."
        self.info(log_message)

        self.transformabe_columns_ = list(X.columns)

        target_n_nans_per_feature = math.ceil(
            self.min_nan_level * len(X))

        log_line = {}
        n_updated_columns = 0
        for f in self.transformabe_columns_:
            a_column = X[f]
            n_values = len(a_column)
            nans = a_column.isna()
            n_nans_before = nans.sum()

            if n_nans_before < target_n_nans_per_feature:
                n_updated_columns += 1
                nans_to_add = target_n_nans_per_feature - n_nans_before
                not_nans = a_column[a_column.notna()]
                set_to_nan_index = not_nans.sample(nans_to_add).index
                X.loc[set_to_nan_index, f] = None

            n_nans_after = X[f].isna().sum()
            assert n_nans_after >= target_n_nans_per_feature

            if n_nans_before < target_n_nans_per_feature:
                n_nans_added = n_nans_after - n_nans_before
            else:
                n_nans_added = 0

            log_line = {"Feature Name": f
                , "# NaN-s Before": n_nans_before
                , "# NaN-s Added": n_nans_added
                , "# NaN-s After": n_nans_after
                , "NaN Level Before": n_nans_before / n_values
                , "NaN Level After": n_nans_after / n_values
                , "total # of values": n_values}
            self.log_df_ = self.log_df_.append(log_line, ignore_index=True)

        if len(log_line):
            self.log_df_ = self.log_df_[list(log_line)]
            self.log_df_.set_index("Feature Name", inplace=True)
            for c in [col for col in self.log_df_ if "#" in col]:
                self.log_df_[c] = self.log_df_[c].astype(int)

        total_nans = int(X.isna().sum().sum())
        total_values = X.shape[0] * X.shape[1]
        nan_level = total_nans / total_values
        log_message = f"<== Returning a new dataframe"
        log_message += f" with shape {X.shape}."
        log_message += f" NaN-s were added to {n_updated_columns} columns."
        log_message += f" The resulting dataset contains {total_nans} NaN-s,"
        log_message += f" which is {nan_level:.2%}"
        log_message += f" of {total_values} values from the new dataframe."
        self.info(log_message)

        return self.finish_transforming(X, write_to_log=False)

    def transform(self
                  , X: pd.DataFrame
                  ) -> pd.DataFrame:
        X = self.start_transforming(X)
        log_message = f"<==Returning exactly the same data with no changes."
        self.info(log_message)
        return self.finish_transforming(X, write_to_log=False)


class Deduper(PFeatureMaker):
    """A transformer that removes duplicated columns (features)"""

    keep: str
    allow_nans: bool
    columns_to_keep_: List[str]
    columns_to_drop_: List[str]

    def __init__(self
                 , keep: str = "first"
                 , allow_nans: bool = False
                 , *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_params(keep, allow_nans)

    def get_params(self, deep=True):
        params = {"keep": self.keep, "allow_nans": self.allow_nans}
        return params

    def set_params(self
                   , keep: str
                   , allow_nans: bool
                   ) -> PFeatureMaker:
        assert keep in {"first", "last"}
        self.keep = keep
        self.allow_nans = allow_nans
        self.columns_to_keep_ = []
        self.columns_to_drop_ = []
        return self

    @property
    def is_fitted_(self) -> bool:
        return bool(len(self.columns_to_keep_))

    @property
    def input_can_have_nans(self) -> bool:
        return self.allow_nans

    @property
    def output_can_have_nans(self) -> bool:
        return self.allow_nans

    @property
    def input_columns_(self) -> List[str]:
        assert self.is_fitted_
        return sorted(self.columns_to_keep_ + self.columns_to_drop_)

    @property
    def output_columns_(self) -> List[str]:
        return sorted(self.columns_to_keep_)

    def fit_transform(self
                      , X: pd.DataFrame
                      , y: Optional[pd.Series] = None
                      ) -> pd.DataFrame:
        X, y = self.start_fitting(X, y)

        X_dd = X.T.drop_duplicates(keep=self.keep).T
        self.columns_to_keep_ = list(X_dd.columns)
        self.columns_to_drop_ = list(set(X.columns) - set(X_dd.columns))

        log_message = f"{len(self.columns_to_drop_)}"
        log_message += f" duplicate features have been removed, "
        log_message += f"{len(self.columns_to_keep_)} unique features left."
        self.info(log_message)

        return self.finish_transforming(X_dd)

    def transform(self
                  , X: pd.DataFrame
                  ) -> pd.DataFrame:
        X = self.start_transforming(X)

        log_message = f"{len(self.columns_to_drop_)}"
        log_message += f" duplicate features have been removed, "
        log_message += f"{len(self.columns_to_keep_)} unique features left."
        self.info(log_message)

        return self.finish_transforming(X[self.output_columns_])


class NumericImputer(PFeatureMaker):
    """A transformer that creates NaN-less versions of numeric columns"""

    aggr_funcs: Optional[List[Any]]
    fill_values_: Optional[pd.DataFrame]

    def __init__(self
                 , aggr_funcs=
                 [np.min, np.max, np.mean, percentile50, minmode, maxmode]
                 , *args
                 , **kwargs
                 ) -> None:
        super().__init__(*args, **kwargs)
        self.set_params(aggr_funcs)

    def get_params(self, deep=True):
        params = {"aggr_funcs": self.aggr_funcs}
        return params

    def set_params(self
                   , aggr_funcs: List[Any]
                   ) -> PFeatureMaker:
        for f in aggr_funcs:
            assert callable(f)
        self.aggr_funcs = aggr_funcs
        self.fill_values_ = None
        return self

    @property
    def is_fitted_(self) -> bool:
        return self.fill_values_ is not None

    @property
    def input_can_have_nans(self) -> bool:
        return True

    @property
    def output_can_have_nans(self) -> bool:
        return False

    @property
    def input_columns_(self) -> List[str]:
        assert self.is_fitted_
        return sorted(self.fill_values_.columns)

    @property
    def output_columns_(self) -> List[str]:
        all_columns = []
        for col in self.input_columns_:
            for f in self.aggr_funcs:
                label = f.__name__
                column_name = "fillna_" + label + "(" + col + ")"
                all_columns += [column_name]

        return sorted(all_columns)

    def fit_transform(self
                      , X: pd.DataFrame
                      , y: Optional[pd.Series] = None
                      ) -> pd.DataFrame:

        type_of_X = type(X).__name__

        X, y = self.start_fitting(X, y, write_to_log=False)

        X_num = X.select_dtypes(include="number")
        num_nans = int(X_num.isna().sum().sum())
        aggr_func_names = [f.__name__ for f in self.aggr_funcs]
        n_func = len(aggr_func_names)

        log_message = f"==> Starting removing NaNs from "
        log_message += f"{len(X_num.columns)} numeric columns of a {type_of_X}"
        log_message += " named < " + NeatStr.object_names(X, div_ch=" / ")
        log_message += f" > with shape {X.shape}. "
        log_message += f"Currently, the numeric columns of a dataset"
        log_message += f" contain {num_nans} NaN-s. "
        log_message += f"Each numeric columns will be replaced with "
        log_message += f"{n_func} new ones, with imputation performed "
        log_message += f"using the following functions: {aggr_func_names}."
        self.info(log_message)

        aggregations = {}
        for col in X_num:
            aggregations[col] = [f(X_num[col]) for f in self.aggr_funcs]

        self.fill_values_ = pd.DataFrame(
            data=aggregations, index=aggr_func_names)
        self.log_df_ = self.fill_values_

        return self.transform(X_num)

    def transform(self
                  , X: pd.DataFrame
                  ) -> pd.DataFrame:

        X = self.start_transforming(X, write_to_log=False)
        X_num = X.select_dtypes(include="number")[self.input_columns_]
        num_nans = X_num.isna().sum().sum()

        all_columns = []
        for col in X_num.columns:
            for f in self.aggr_funcs:
                label = f.__name__
                f_val = self.fill_values_.at[label, col]
                filled_column = X_num[col].fillna(value=f_val)
                filled_column.name = "fillna_" + label + "(" + col + ")"
                all_columns += [filled_column]

        result = pd.concat(all_columns, axis=1)
        log_message = f"<== Returning a new, numeric-only dataframe"
        log_message += f" with shape {result.shape}."
        log_message += f" {num_nans} original NaN-s were removed"
        log_message += f" by applying {len(self.aggr_funcs)}"
        log_message += f" imputation functions."
        self.info(log_message)

        return self.finish_transforming(result, write_to_log=False)


class NumericFuncTransformer(PFeatureMaker):
    """A transformer that applies math functions to numeric features"""

    columns_to_a_transform_: Optional[List[str]]
    columns_to_p_transform_: Optional[List[str]]
    positive_arg_functions: List[Any]
    any_arg_functions: List[Any]

    def __init__(self
                 , positive_arg_functions=[np.log1p, root2, power2]
                 , any_arg_functions=[passthrough, power3]
                 , *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_params(positive_arg_functions, any_arg_functions)

    def get_params(self, deep=True):
        params = {"positive_arg_functions": self.positive_arg_functions
            , "any_arg_functions": self.any_arg_functions}
        return params

    def set_params(self
                   , positive_arg_functions
                   , any_arg_functions
                   ) -> PFeatureMaker:

        for f in positive_arg_functions + any_arg_functions:
            assert callable(f)

        self.positive_arg_functions = positive_arg_functions
        self.any_arg_functions = any_arg_functions
        self.columns_to_p_transform_ = None
        self.columns_to_a_transform_ = None
        return self

    @property
    def is_fitted_(self):
        result = (self.columns_to_a_transform_ is not None
                  and self.columns_to_p_transform_ is not None)
        return result

    @property
    def input_can_have_nans(self) -> bool:
        return True

    @property
    def output_can_have_nans(self) -> bool:
        return True

    @property
    def input_columns_(self) -> List[str]:
        assert self.is_fitted_
        return sorted(set(self.columns_to_a_transform_)
                      | set(self.columns_to_p_transform_))

    @property
    def output_columns_(self) -> List[str]:

        all_columns = []

        for a_func in self.any_arg_functions:
            f_columns = [a_func.__name__ + "(" + c + ")"
                         for c in self.columns_to_a_transform_]
            all_columns += f_columns

        for p_func in self.positive_arg_functions:
            f_columns = [p_func.__name__ + "(" + c + ")"
                         for c in self.columns_to_p_transform_]
            all_columns += f_columns

        return sorted(all_columns)

    def fit_transform(self
                      , X: pd.DataFrame
                      , y: Optional[pd.Series] = None
                      ) -> pd.DataFrame:

        (X, y) = self.start_fitting(X, y)

        self.columns_to_p_transform_ = None
        self.columns_to_a_transform_ = None

        X_numbers = X.select_dtypes(include="number")
        assert len(X_numbers.columns)
        self.columns_to_a_transform_ = list(X_numbers.columns)

        feature_mins = X_numbers.min()
        p_transformable_features = feature_mins[feature_mins >= 0]
        self.columns_to_p_transform_ = list(p_transformable_features.index)

        result = self.transform(X)

        return result

    def transform(self
                  , X: pd.DataFrame
                  ) -> pd.DataFrame:

        all_funcs = self.positive_arg_functions + self.any_arg_functions
        all_funcs = [f.__name__ for f in all_funcs]

        X_numbers = self.start_transforming(
            X, write_to_log=False).select_dtypes("number")

        log_message = f"==> Starting generating features "
        log_message += f"using a {type(X).__name__} named < "
        log_message += NeatStr.object_names(X, div_ch=" / ")
        log_message += f" > with the shape {X.shape} and the following "
        log_message += f"{len(all_funcs)} functions: {all_funcs}."
        self.info(log_message)

        all_transformations = []

        for a_func in self.any_arg_functions:
            X_new = a_func(X_numbers)
            X_new.columns = [a_func.__name__ + "(" + c + ")" for c in X_new]
            all_transformations += [X_new]

        if len(self.columns_to_p_transform_):
            X_positive_numbers = deepcopy(
                X_numbers[self.columns_to_p_transform_])
            negative_flags = (X_positive_numbers < 0)
            below_zero = negative_flags.sum().sum()
            X_positive_numbers[negative_flags] = 0

            if below_zero > 0:
                log_message = f"{below_zero} negative values were found in "
                log_message += "the features, scheduled for transformation "
                log_message += "via functions that expect positive input "
                log_message += "values. Negatives will be replaced "
                log_message += "with zeros."
                self.warning(log_message)

            for p_func in self.positive_arg_functions:
                X_new = p_func(X_positive_numbers)
                X_new.columns = [p_func.__name__ + "(" + c + ")" for c in
                                 X_new]
                all_transformations += [X_new]

        result = pd.concat(all_transformations, axis=1)

        return self.finish_transforming(result)

class CatSelector(PFeatureMaker):
    """ Abstract base class that finds categorical features"""

    min_cat_size: int
    max_uniques: int
    cat_columns_: Optional[Set[str]]
    cat_values_: Optional[Dict[str, Set[str]]]

    def __init__(self
                 , min_cat_size: int = 20
                 , max_uniques: int = 100
                 , *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_params(min_cat_size, max_uniques)

    def get_params(self, deep=True):
        params = {"min_cat_size": self.min_cat_size
            , "max_uniques": self.max_uniques}
        return params

    def set_params(self
                   , min_cat_size
                   , max_uniques, **kwards):
        self.min_cat_size = min_cat_size
        self.max_uniques = max_uniques
        self.cat_columns_ = None
        self.cat_values_ = None
        return self

    def start_fitting(self
                      , X: Any
                      , y: Any
                      , write_to_log: bool = True
                      ) -> pd.DataFrame:

        X, y = super().start_fitting(X, y, write_to_log)
        uniques = X.nunique()
        uniques = uniques[uniques <= self.max_uniques]

        self.cat_columns_ = set(uniques.index)
        self.cat_values_ = dict()

        for c in self.cat_columns_:
            uniques = X[c].value_counts()
            uniques = uniques[uniques >= self.min_cat_size]
            self.cat_values_[c] = set(uniques.index)
            if len(self.cat_values_[c]) == 0:
                del self.cat_values_[c]

        self.cat_columns_ = set(self.cat_values_)

        X = deepcopy(X[self.cat_columns_])

        for col in X:
            nan_idx = ~ X[col].isin(self.cat_values_[col])
            X.loc[nan_idx, col] = None

        return X, y

    def start_transforming(self
                           , X: pd.DataFrame
                           , write_to_log: bool = True
                           ) -> pd.DataFrame:
        X = super().start_transforming(X,  write_to_log)

        for col in X:
            nan_idx = ~ X[col].isin(self.cat_values_[col])
            X.loc[nan_idx, col] = None

        return X



class TargetMultiEncoder(CatSelector):
    pass


class TargetMultiEncoder(CatSelector):
    tme_agg_funcs: List[Any]
    tme_cat_values_: Optional[Dict[str, pd.DataFrame]]
    tme_default_values_: Optional[Dict[str, float]]
    nan_string:str

    def __init__(self
                 , min_cat_size=20
                 , max_uniques=100
                 , agg_funcs=[
                        percentile05
                        , percentile25
                        , percentile50
                        , percentile75
                        , percentile95
                        , minmode
                        , maxmode]
                 , *args
                 , **kwargs
                 ) -> None:
        super().__init__(*args, **kwargs)
        self.set_params(min_cat_size, max_uniques, agg_funcs)

    def get_params(self, deep=True):
        params = super().get_params(deep)
        params["tme_agg_funcs"] = self.tme_agg_funcs
        return params

    def set_params(self
                   , min_cat_size
                   , max_uniques
                   , tme_agg_funcs = None
                   ):
        super().set_params(min_cat_size, max_uniques)
        self.tme_agg_funcs = deepcopy(tme_agg_funcs)
        self.tme_cat_values_ = None
        self.tme_default_values_ = None
        self.nan_string: str = "<<<<-----TME-NaN----->>>>:" + str(id(self))
        return self

    @property
    def is_fitted_(self):
        return self.tme_default_values_ is not None

    @property
    def input_can_have_nans(self) -> bool:
        return True

    @property
    def output_can_have_nans(self) -> bool:
        return False

    @property
    def input_columns_(self) -> List[str]:
        return sorted(self.tme_cat_values_)

    @property
    def output_columns_(self) -> List[str]:
        assert self.is_fitted_
        return sorted([self.tme_column_name(f, c)
                       for c in self.tme_cat_values_ for f in
                       self.tme_agg_funcs])

    def tme_column_name(self, func, column: str) -> str:
        if callable(func):
            func = func.__name__
        name = "targ_enc_" + func + "(" + column + ")"
        return name

    def convert_X(self, X: pd.DataFrame) -> pd.DataFrame:
        
        assert set(X.columns) == set(self.cat_columns_)

        for cat in X:
            X[cat] = X[cat].astype("object")

        X.fillna(self.nan_string, inplace=True)

        for cat in self.cat_values_:
            self.cat_values_[cat] |= {self.nan_string}
            nan_idx = ~ (X[cat].isin(self.cat_values_[cat]))
            X.loc[nan_idx, cat] = self.nan_string

        return X

    def fit_transform(self
                      , X: pd.DataFrame
                      , y
                      ) -> TargetMultiEncoder:

        X, y = self.start_fitting(X, y)

        X = self.convert_X(X)

        assert len(X) == len(y)

        log_message = f"A total of {len(X.columns)} features "
        log_message += f"will be encoded using {len(self.tme_agg_funcs)} "
        log_message += f"functions: {[f.__name__ for f in self.tme_agg_funcs]}."
        self.info(log_message)

        columns = deepcopy(X.columns)
        taget_name = "TAGET_" + y.name + "_TARGET"
        assert taget_name not in columns
        X[taget_name] = y

        self.tme_default_values_ = {}
        self.tme_cat_values_ = {}
        for f in self.tme_agg_funcs:
            self.tme_default_values_[f] = f(X[taget_name])

        for col in columns:

            v = pd.pivot_table(X[[col, taget_name]]
                               , values=taget_name
                               , index=col
                               , aggfunc=self.tme_agg_funcs
                               , dropna=False)

            n_nans = v.isna().sum().sum()
            if n_nans:
                log_message = f"Got {n_nans} NaN-s while generating "
                log_message += f"target encoding values for {col}."
                log_message += " Replacing with default values."
                self.warning(log_message)

            for i in range(len(self.tme_agg_funcs)):
                a_func = self.tme_agg_funcs[i]
                def_value = self.tme_default_values_[a_func]
                v[v.columns[i]] = v[v.columns[i]].fillna(def_value)

            v.columns = [
                self.tme_column_name(c[0], col) for c in v.columns]

            self.tme_cat_values_[col] = v

        X.drop(columns=taget_name, inplace=True)

        result = self.transform(X)

        return result

    def transform(self
                  , X: pd.DataFrame
                  ) -> pd.DataFrame:

        X = self.start_transforming(X)

        X = self.convert_X(X)

        columns = deepcopy(X.columns)

        for col in X.columns:

            index_col_name = "____>>__INDEX_<<_____"+str(id(self))
            X[index_col_name] = X.index
            X = X.merge(self.tme_cat_values_[col], on=col, how="inner")
            X.index = X[index_col_name]
            X.drop(columns=index_col_name, inplace = True)

            for i in range(len(self.tme_agg_funcs)):
                a_func = self.tme_agg_funcs[i]
                a_column = self.tme_column_name(a_func, col)
                def_value = self.tme_default_values_[a_func]
                n_nans = X[a_column].isna().sum()
                if n_nans:
                    log_message = f"Found {n_nans} NaN-s in column {a_column}"
                    log_message += f" after replacing know values"
                    log_message += f" with targed-encodings,"
                    log_message += f" filling NaN-s with default value."
                    self.warning(log_message)
                    X[a_column] = X[a_column].fillna(def_value)

            X.drop(columns=col, inplace=True)

        return self.finish_transforming(X)


class LOOMeanTargetEncoder(CatSelector):
    """Leave-One-Out Mean Target Encoder for categorical features"""

    encodable_columns_: Optional[Set[str]]
    sums_counts_: Optional[Dict[str, Dict[str, float]]]
    nan_string:str

    def __init__(self
                 , min_cat_size: int = 20
                 , max_uniques: int = 100
                 , *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_params(min_cat_size, max_uniques)

    def get_params(self, deep=True):
        params = super().get_params(deep)
        return params

    def set_params(self
                   , min_cat_size
                   , max_uniques):
        super().set_params(min_cat_size, max_uniques)
        self.sums_counts_ = None
        self.encodable_columns_ = None
        self.nan_string: str = "<<<<-----LOO-NaN----->>>>:" + str(id(self))
        return self

    @property
    def is_fitted_(self):
        return self.sums_counts_ is not None

    @property
    def input_can_have_nans(self) -> bool:
        return True

    @property
    def output_can_have_nans(self) -> bool:
        return False

    @property
    def input_columns_(self) -> List[str]:
        return sorted(self.encodable_columns_)

    @property
    def output_columns_(self) -> List[str]:
        return sorted(["LOOMean(" + c + ")" for c in self.input_columns_])

    def fit_transform(self
                      , X: pd.DataFrame
                      , y: pd.Series
                      ) -> pd.DataFrame:

        X, y = self.start_fitting(X, y)
        X.fillna()

        self.sums_counts_ = dict()

        for c in self.cat_columns_:
            self.sums_counts_[c] = dict()
            for v in set(self.cat_values_[c]):
                ix = (X[c] == v)
                self.sums_counts_[c][v] = (y[ix].sum(), ix.sum())

        X = X[self.cat_columns_]

        nontrivial = X.nunique()
        nontrivial = nontrivial[nontrivial > 1]
        self.encodable_columns_ = set(nontrivial.index)
        to_delete = set(self.cat_columns_) - set(self.encodable_columns_)
        for c in to_delete:
            del self.sums_counts_[c]

        for c in self.sums_counts_:
            vals = np.full(len(X), np.nan)
            for cat, sum_count in self.sums_counts_[c].items():
                #                 if not sum_count[1]>1:
                #                     self.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!! not sum_count[1]>1")
                ix = (X[c] == cat)
                vals[ix] = (sum_count[0] - y[ix]) / (sum_count[1] - 1)
            X[c] = vals

        X = X[self.encodable_columns_]
        X.columns = ["LOOMean(" + c + ")" for c in X.columns]

        return self.finish_transforming(X)

    def transform(self
                  , X: pd.DataFrame
                  ) -> pd.DataFrame:

        X = self.start_transforming(X)

        for c in self.input_columns_:
            vals = np.full(len(X), np.nan)
            for cat, sum_count in self.sums_counts_[c].items():
                #                 if not sum_count[1]>0:
                #                     self.error("!!!!!!!!!!!!!!!!!!!!!!!!!!!! not sum_count[1]>0")
                vals[X[c] == cat] = sum_count[0] / sum_count[1]
            X[c] = vals

        X.columns = ["LOOMean(" + c + ")" for c in X.columns]

        return self.finish_transforming(X)


class DummiesMaker(CatSelector):
    dummy_names_: Optional[str]

    def __init__(self
                 , min_cat_size: int = 20
                 , max_uniques: int = 100
                 , *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_params(min_cat_size, max_uniques)

    def get_params(self, deep=True):
        params = super().get_params(deep)
        return params

    def set_params(self
                   , min_cat_size
                   , max_uniques):
        super().set_params(min_cat_size, max_uniques)
        self.dummy_names_ = None
        return self

    @property
    def is_fitted_(self):
        return self.dummy_names_ is not None

    @property
    def input_can_have_nans(self) -> bool:
        return True

    @property
    def output_can_have_nans(self) -> bool:
        return False

    @property
    def input_columns_(self) -> List[str]:
        return sorted(self.cat_columns_)

    @property
    def output_columns_(self) -> List[str]:
        return sorted(self.dummy_names_)

    def _get_dummies(self, feature: pd.Series) -> pd.DataFrame:

        all_dummies = []
        new_dummy = feature.isna().astype(int)
        new_dummy.name = f"{feature.name}==eNaN"
        all_dummies += [new_dummy]

        for val in self.cat_values_[feature.name]:
            new_dummy = (feature == val).astype(int)
            new_dummy.name = f"{feature.name}=={str(val)}"
            all_dummies += [new_dummy]

        result = pd.concat(all_dummies, axis=1)

        return result

    def fit_transform(self
                      , X: pd.DataFrame
                      , y=None
                      ) -> pd.DataFrame:

        X, y = self.start_fitting(X, y)

        all_dummies = []

        for col in self.cat_columns_:
            all_dummies += [self._get_dummies(X[col])]

        result = pd.concat(all_dummies, axis=1)

        self.dummy_names_ = list(result.columns)

        return self.finish_transforming(result)

    def transform(self
                  , X: pd.DataFrame
                  ) -> pd.DataFrame:

        X = self.start_transforming(X)

        all_dummies = []

        for col in self.cat_columns_:
            all_dummies += [self._get_dummies(X[col])]

        result = pd.concat(all_dummies, axis=1)

        return self.finish_transforming(result)



class FeatureShower(PFeatureMaker):
    pass


class FeatureShower(PFeatureMaker):
    is_fitted_flag_: bool

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_params()

    def set_params(self, deep: bool = False) -> FeatureShower:
        self.nan_inducer = NaN_Inducer()
        self.dummies_maker = DummiesMaker()
        self.numeric_func_trnsf = NumericFuncTransformer()
        self.numeric_imputer = NumericImputer()
        self.target_multi_encoder = TargetMultiEncoder()
        self.deduper = Deduper()
        self.is_fitted_flag_ = False
        return self

    def get_params(self, deep: bool = False) -> Dict[str, Any]:
        return {}

    @property
    def is_fitted_(self):
        return self.is_fitted_flag_


    @property
    def input_columns_(self) -> List[str]:
        return self.nan_inducer.input_columns_


    @property
    def output_columns_(self) -> List[str]:
        return self.deduper.output_columns_

    @property
    def input_can_have_nans(self) -> bool:
        return True

    @property
    def output_can_have_nans(self) -> bool:
        return False

    def fit_transform(self
                      , X:pd.DataFrame
                      , y:pd.Series
                      ) -> pd.DataFrame:
        X, y = self.start_fitting(X, y)

        X_with_NaNs = self.nan_inducer.fit_transform(X, y)

        X_numeric_tr = self.numeric_func_trnsf.fit_transform(X_with_NaNs, y)
        X_numeric_no_NaNs = self.numeric_imputer.fit_transform(X_numeric_tr, y)

        X_dummies = self.dummies_maker.fit_transform(X_with_NaNs,y)

        X_target_encoded_cats = self.target_multi_encoder.fit_transform(
            X_with_NaNs, y)

        X_full = pd.concat(
            [X_numeric_no_NaNs, X_target_encoded_cats, X_dummies], axis=1)

        X_final = self.deduper.fit_transform(X_full, y)

        self.is_fitted_flag_ = True

        return self.finish_transforming(X_final)


    def transform(self, X):
        X = self.start_transforming(X)

        X_with_NaNs = self.nan_inducer.transform(X)

        X_numeric_tr = self.numeric_func_trnsf.transform(X_with_NaNs)
        X_numeric_no_NaNs = self.numeric_imputer.transform(X_numeric_tr)

        X_dummies = self.dummies_maker.transform(X_with_NaNs)
        for c in X_dummies:
            X_dummies[c] =1

        X_target_encoded_cats = self.target_multi_encoder.transform(
            X_with_NaNs)
        X_full = pd.concat(
            [X_numeric_no_NaNs, X_target_encoded_cats,X_dummies], axis=1)

        X_final = self.deduper.transform(X_full)

        return self.finish_transforming(X_final)
