import pandas as pd

from Pythagoras.util import *
from Pythagoras.logging import *
from Pythagoras.feature_engineering import *



# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation



class CV_Score(LoggableObject):
    def __init__(self, model, n_splits=3, n_repeats=3):
        self.rkf = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats)
        self.model = clone(model)

    def __call__(self, X, y, ):
        self.scores_ = cross_val_score(self.model, X, y, cv=self.rkf,
                                       scoring="r2")
        mean_score = np.mean(self.scores_)
        median_score = np.median(self.scores_)
        return min(mean_score, median_score)


class PRegressor(PEstimator):
    target_name_: Optional[str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start_fitting(self
                      , X: Any
                      , y: Any
                      , write_to_log: bool = True
                      ) -> Tuple[pd.DataFrame, pd.Series]:
        X, y = super().start_fitting(X, y)
        self.target_name_ = y.name
        self.min_med_max_ = (min(y), percentile50(y), max(y))
        return X, y

    def start_predicting(self
                         , X: pd.DataFrame
                         , write_to_log: bool = True
                         ) -> pd.DataFrame:

        assert self.is_fitted_
        assert len(X)

        if write_to_log:
            log_message = f"==> Starting generating predictions "
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

    def finish_predicting(self
                          , y: pd.Series
                          , write_to_log: bool = True
                          ) -> pd.DataFrame:

        assert len(y)

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

        if not self.output_can_have_nans:
            assert n_nans == 0

        y.name = self.target_name_

        return y


