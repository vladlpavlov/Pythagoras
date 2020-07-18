import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List

from numpy import mean, median
from sklearn import clone
from sklearn.model_selection import cross_val_score, RepeatedKFold

from Pythagoras.util import *
from Pythagoras.logging import *
from Pythagoras.caching import *
from Pythagoras.feature_engineering import *
from Pythagoras.regression import *

# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
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

        if isinstance(X, pd.DataFrame):
            X = deepcopy(X)
        else:
            X = pd.DataFrame(X, copy=True)

        if type(X.columns[0]) != str:
            X.columns = ["col_"+str(c) for c in X.columns]

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
        else:
            y = None

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

    def fit_transform(self
            ,X:pd.DataFrame
            ,y:Optional[pd.Series]=None
            ) -> pd.DataFrame:

        if type(self) == AbstractFeatureMaker:
            raise NotImplementedError

        if y is not None:
            X.sort_index(inplace=True)
            y.sort_index(inplace=True)
            assert (X.index == y.index).all()

        return X

    def transform(self
            ,X:pd.DataFrame
            ) -> pd.DataFrame:
        raise NotImplementedError

    @property
    def is_fitted(self) -> bool:
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

        X, y = self.start_fitting(X, y, write_to_log=False)

        X_num = X.select_dtypes(include="number")
        num_nans = int(X_num.isna().sum().sum())
        aggr_func_names = [f.__name__ for f in self.aggr_funcs]
        n_func = len(aggr_func_names)

        log_message = f"==> Starting removing NaNs from "
        log_message += f"{len(X_num.columns)} numeric columns of a dataframe "
        log_message += "named < " + NeatStr.object_names(X, div_ch=" / ")
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
                 , any_arg_functions=[power3]
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
        self.columns_to_p_transform = None
        self.columns_to_a_transform = None
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
                      ) -> pd.core.frame.DataFrame:

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
                  , X: pd.core.frame.DataFrame
                  ) -> pd.core.frame.DataFrame:

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