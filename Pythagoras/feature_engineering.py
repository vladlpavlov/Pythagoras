import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List

from numpy import mean, median

from Pythagoras.util import *
from Pythagoras.logging import *

# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
class AbstractFeatureMaker(LoggableObject):
    pass

class AbstractFeatureMaker(LoggableObject):
    """A base class for transformers that create new features"""

    def __init__(self,  *args, **kwargs) -> None:
        kwargs["reveal_calling_method"] = kwargs.get(
            "reveal_calling_method", True)
        super().__init__(*args, **kwargs)

    def fit(self
            ,X:pd.core.frame.DataFrame
            ,y=None
            ) -> pd.core.frame.DataFrame:
        raise NotImplementedError

    def stack_fit(self
            ,base_transformer: AbstractFeatureMaker
            ) -> pd.core.frame.DataFrame:
        """Fit a transformer using another, already fitted transformer"""
        raise NotImplementedError

    def fit_transform(self
            ,X:pd.core.frame.DataFrame
            ,y=None
            ) -> pd.core.frame.DataFrame:
        raise NotImplementedError

    def transform(self
            ,X:pd.core.frame.DataFrame
            ) -> pd.core.frame.DataFrame:
        raise NotImplementedError

    @property
    def is_fitted(self) -> bool:
        raise NotImplementedError


class NaN_Inducer(AbstractFeatureMaker):
    """A transformer that adds random NaN-s to a dataset"""

    log_df: Optional[pd.core.frame.DataFrame]
    columns: Set[str]
    min_nan_level: float

    def __init__(self, min_nan_level: float = 0.05, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert 0 <= min_nan_level < 1
        self.min_nan_level = min_nan_level
        self.log_df = None
        self.columns = set()

    @property
    def is_fitted(self) -> bool:
        return bool(len(self.columns))

    def fit_transform(self
            , X: pd.core.frame.DataFrame
            , y = None
            ) -> pd.core.frame.DataFrame:
        self.log_df = pd.DataFrame()
        total_nans = int(X.isna().sum().sum())
        total_values = X.shape[0] * X.shape[1]
        current_nan_level = total_nans / total_values
        log_message = f"==> Starting adding random NaNs to a copy of dataframe "
        log_message += "named < " + NeatStr.object_names(X, div_ch=" / ")
        log_message += f" > with shape {X.shape}, aiming to reach "
        log_message += f"{self.min_nan_level:.2%} level for each column. "
        log_message += f"Currently the dataset contains {total_nans} NaN-s,"
        log_message += f" which is {current_nan_level:.2%}"
        log_message += f" of {total_values} values from the dataframe."
        self.info(log_message)

        self.columns = set(X.columns)

        X_new = deepcopy(X)
        features = list(X_new.columns)
        target_n_nans_per_feature = math.ceil(
            self.min_nan_level * len(X))

        log_line = {}
        n_updated_columns = 0
        for f in features:
            a_column = X_new[f]
            n_values = len(a_column)
            nans = a_column.isna()
            n_nans_before = nans.sum()

            if n_nans_before < target_n_nans_per_feature:
                n_updated_columns += 1
                nans_to_add = target_n_nans_per_feature - n_nans_before
                not_nans = a_column[a_column.notna()]
                set_to_nan_index = not_nans.sample(nans_to_add).index
                X_new.loc[set_to_nan_index, f] = None
            n_nans_after = X_new[f].isna().sum()
            assert n_nans_after >= target_n_nans_per_feature

            if n_nans_before < target_n_nans_per_feature:
                n_nans_added = n_nans_after - n_nans_before
            else:
                n_nans_added = 0

            log_line = {"Feature Name": f
                , "# NaN-s Added": n_nans_added
                , "# NaN-s Before": n_nans_before
                , "# NaN-s After": n_nans_after
                , "total # of values": n_values
                , "NaN Level Before": n_nans_before / n_values
                , "NaN Level After": n_nans_after / n_values}
            self.log_df = self.log_df.append(log_line, ignore_index=True)

        self.log_df.set_index("Feature Name", inplace=True)
        if len(log_line):
            for c in list(log_line)[1:-2]:
                self.log_df[str(c)] = self.log_df[str(c)].astype(int)

        total_nans = int(X_new.isna().sum().sum())
        total_values = X_new.shape[0] * X.shape[1]
        nan_level = total_nans / total_values
        log_message = f"<== Returning a new dataframe"
        log_message += f" with shape {X_new.shape}."
        log_message += f" NaN-s were added to {n_updated_columns} columns."
        log_message += f" The resulting dataset contains {total_nans} NaN-s,"
        log_message += f" which is {nan_level:.2%}"
        log_message += f" of {total_values} values from the new dataframe."
        self.info(log_message)

        return X_new

    def transform(self
            , X: pd.core.frame.DataFrame
            ) -> pd.core.frame.DataFrame:
        log_message = "==> A dataframe named < "
        log_message += NeatStr.object_names(X, div_ch=" / ")
        log_message += f" > with shape {X.shape} and"
        log_message += f" {int(X.isna().sum().sum())} NaN-s has been received."
        self.info(log_message)

        assert self.log_df is not None
        assert set(X.columns) == self.columns

        log_message = f"<== Returning exactly the same dataframe with no changes."
        self.info(log_message)
        return X


class Deduper(AbstractFeatureMaker):
    """A transformer that removes duplicated columns (features)"""

    keep:str
    columns_to_keep: List[str]
    columns_to_drop: List[str]

    def __init__(self, keep="first", *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        assert keep in {"first","last"}
        self.keep=keep
        self.columns_to_keep = []
        self.columns_to_drop = []

    @property
    def is_fitted(self) -> bool:
        return bool(len(self.columns_to_keep))

    def fit_transform(self
            , X: pd.core.frame.DataFrame
            , y=None
            ) -> pd.core.frame.DataFrame:
        log_message = f"==> Starting discovering and removing duplicate "
        log_message += "features from a dataframe named < "
        log_message += NeatStr.object_names(X, div_ch=" / ")
        log_message += f" > with the shape {X.shape}."
        self.info(log_message)

        X.columns = list(X.columns)
        X_new = X.T.drop_duplicates(keep=self.keep).T
        self.columns_to_keep = list(X_new.columns)
        self.columns_to_drop = list(set(X.columns) - set(X_new.columns))

        log_message = f"<== Dedup has finished, {len(self.columns_to_drop)}"
        log_message += f" duplicate features have been removed, "
        log_message += f"{len(self.columns_to_keep)} unique features left."
        self.info(log_message)
        return X_new

    def transform(self
            , X: pd.core.frame.DataFrame
            ) -> pd.core.frame.DataFrame:
        assert len(self.columns_to_keep)
        assert set(self.columns_to_keep) <= set(X.columns)
        assert set(self.columns_to_drop) < set(X.columns)
        X_new = deepcopy(X[self.columns_to_keep])

        # TODO: add check whether the columns to drop are actually duplicates

        log_message = f"A dataframe named < "
        log_message += NeatStr.object_names(X, div_ch=" / ")
        log_message += f" > with the shape {X.shape} "
        log_message += f"has been transformed by removing"
        log_message += f" {len(self.columns_to_drop)} duplicate features."
        self.info(log_message)

        return X_new


class NumericImputer(AbstractFeatureMaker):
    """A transformer that creates NaN-less versions of numeric columns"""

    nan_aggr_funcs: Optional[List[Any]]
    nan_fill_values: Optional[pd.core.frame.DataFrame]

    def __init__(self
             , aggr_funcs =
                [np.min, np.max, np.mean, percentile50 , minmode, maxmode]
             , *args
             , **kwargs
             ) -> None:
        super().__init__(*args, **kwargs)
        self.nan_fill_values = None
        self.nan_aggr_funcs = aggr_funcs


    @property
    def is_fitted(self) -> bool:
        return self.nan_fill_values is not None

    def fit_transform(self
            , X: pd.core.frame.DataFrame
            , y=None
            ) -> pd.core.frame.DataFrame:

        X_num = X.select_dtypes(include="number")
        num_nans = int(X_num.isna().sum().sum())
        aggr_func_names = [f.__name__ for f in self.nan_aggr_funcs]
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
            aggregations[col] = [f(X_num[col]) for f in self.nan_aggr_funcs]

        self.nan_fill_values = pd.DataFrame(
            data=aggregations, index=aggr_func_names)
        print()
        return self.transform(X_num)

    def transform(self
            , X: pd.core.frame.DataFrame
            ) -> pd.core.frame.DataFrame:

        assert self.is_fitted
        X_num = X.select_dtypes(include="number")
        assert set(X_num.columns) == set(self.nan_fill_values.columns)
        num_nans = X_num.isna().sum().sum()

        all_columns = []
        for col in X_num.columns:
            for f in self.nan_aggr_funcs:
                label = f.__name__
                f_val = self.nan_fill_values.at[label, col]
                filled_column = X[col].fillna(value=f_val)
                filled_column.name = "fillna_" + label + "(" + col + ")"
                all_columns += [filled_column]

        result = pd.concat(all_columns, axis=1)
        log_message = f"<== Returning a new, numeric-only dataframe"
        log_message += f" with shape {result.shape}."
        log_message += f" {num_nans} original NaN-s were removed"
        log_message += f" by applying {len(self.nan_aggr_funcs)}"
        log_message += f" imputation functions."
        self.info(log_message)
        return result