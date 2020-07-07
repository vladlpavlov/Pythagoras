import pandas as pd
from copy import deepcopy
from typing import Optional, Set
from Pythagoras.util import *
from Pythagoras.logging import *



class AbstractFeatureMaker(LoggableObject):
    """An base class for transformers that create new features"""

    def __init__(self,  *args, **kwargs) -> None:
        kwargs["reveal_calling_method"] = kwargs.get(
            "reveal_calling_method", True)
        super().__init__(*args, **kwargs)

    def fit_transform(self
            ,X:pd.core.frame.DataFrame
            ,y=None
            ) -> pd.core.frame.DataFrame:
        raise NotImplementedError

    def transform(self
            ,X:pd.core.frame.DataFrame
            ) -> pd.core.frame.DataFrame:
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