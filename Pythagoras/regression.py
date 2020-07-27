import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.model_selection import cross_validate

from Pythagoras.util import *
from Pythagoras.logging import *
from Pythagoras.feature_engineering import *
from Pythagoras.caching import *


# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation



class CV_Score(LoggableObject):
    """Cross-validation score calculator"""

    def __init__(self
            , model
            , n_splits=5
            , n_repeats=4
            , random_state = None
            ,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.rkf = RepeatedKFold(
            n_splits=n_splits
            , n_repeats=n_repeats
            , random_state = random_state)

        self.model = update_param_if_supported(
            model,"random_state",random_state )

    def __call__(self, X, y, **kwargs):
        self.scores_ = cross_val_score(
            self.model, X, y, cv=self.rkf, scoring="r2", **kwargs)
        mean_score = np.mean(self.scores_)
        median_score = np.median(self.scores_)
        return min(mean_score, median_score)


class PRegressor(PEstimator):
    """ Abstract base class for all Pythagoras regressors.

    Warning: This class should not be used directly. Use derived classes
    instead.
    """

    target_name_: Optional[str]
    prediction_index_:Optional[pd.Series]

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

    def predict(self, X:pd.DataFrame) -> pd.Series:
        raise NotImplementedError

    def start_predicting(self
                         , X: pd.DataFrame
                         , write_to_log: bool = True
                         ) -> pd.DataFrame:

        if write_to_log:
            log_message = f"==> Starting generating predictions "
            log_message += f"using a {type(X).__name__} named < "
            log_message += NeatStr.object_names(X, div_ch=" / ")
            log_message += f" > with the shape {X.shape}."
            self.info(log_message)

        assert self.is_fitted_
        X = self._preprocess_X(X)
        self.prediction_index_ = deepcopy(X.index)

        if self.input_columns_ is NotProvided:
            self.warning("Attribute input_columns_ was not provided.")
        else:
            assert set(self.input_columns_) <= set(X)
            X = deepcopy(X[self.input_columns_])

        return X

    def finish_predicting(self
                          , y: pd.Series
                          , write_to_log: bool = True
                          ) -> pd.Series:

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

        assert len(y)
        assert len(y) == len(self.prediction_index_)

        if self.output_can_have_nans is NotProvided:
            self.warning("Attribute output_can_have_nans was not provided.")
        elif not self.output_can_have_nans:
            assert n_nans == 0

        y.name = self.target_name_
        y.index = self.prediction_index_

        return y


class SimpleGarden(PRegressor):

    def __init__(self
                 , garden_base_model=LinearRegression(normalize=True)
                 , garden_feature_cr_threshold: float = 0.5
                 , max_features_per_pmodel: Optional[int] = None
                 , max_pmodels_per_garden: int = 15
                 , garden_cv_score_threshold: Optional[float] = None
                 , garden_cv_score_threshold_multiplier: Optional[float] = 0.8
                 , random_state = None
                 , **kwargs
                 ) -> None:

        super().__init__( **kwargs)
        self.set_params(garden_base_model=garden_base_model
            , garden_feature_cr_threshold=garden_feature_cr_threshold
            , max_features_per_pmodel=max_features_per_pmodel
            , max_pmodels_per_garden=max_pmodels_per_garden
            , garden_cv_score_threshold=garden_cv_score_threshold
            , garden_cv_score_threshold_multiplier=garden_cv_score_threshold_multiplier
            , random_state = random_state)

    def set_params(self
                   , garden_base_model = None
                   , garden_feature_cr_threshold = None
                   , max_features_per_pmodel = None
                   , max_pmodels_per_garden = None
                   , garden_cv_score_threshold = None
                   , garden_cv_score_threshold_multiplier = None
                   , random_state = None
                   , **kwargs
                   ) -> PRegressor:

        self.garden_base_model = garden_base_model
        self.base_model_cv_score = None

        self.garden_feature_cr_threshold = garden_feature_cr_threshold
        self.max_features_per_pmodel = max_features_per_pmodel
        self.max_pmodels_per_garden = max_pmodels_per_garden
        self.garden_cv_score_threshold = garden_cv_score_threshold
        self.garden_cv_score_threshold_multiplier = garden_cv_score_threshold_multiplier

        self.pmodels_ = []
        self.feature_lists_ = []
        self.cv_scores_ = []
        self.log_df_ = None
        self.fit_cv_score_threshold_ = None
        self.random_state = random_state

        return self

    def get_params(self, deep: bool = False) -> Dict[str, Any]:

        result = {"garden_base_model": self.garden_base_model
            ,"garden_feature_cr_threshold": self.garden_feature_cr_threshold
            ,"max_features_per_pmodel": self.max_features_per_pmodel
            ,"max_pmodels_per_garden": self.max_pmodels_per_garden
            ,"garden_cv_score_threshold": self.garden_cv_score_threshold
            ,"garden_cv_score_threshold_multiplier": self.garden_cv_score_threshold_multiplier
            ,"random_state": self.random_state}

        return result

    @property
    def input_columns_(self) -> List[str]:
        return sorted([c for l in self.feature_lists_ for c in l])

    @property
    def input_can_have_nans(self) -> bool:
        return False

    @property
    def output_can_have_nans(self) -> bool:
        return False

    def one_best_feature(self
                         , X: pd.DataFrame
                         , y: pd.Series
                         ) -> Tuple[str, float]:
        cr = pd.DataFrame(np.abs(X.corrwith(y)))
        cr.sort_values(by=cr.columns[0], ascending=False, inplace=True)
        best_feature = cr.index[0]
        corr_best_feature = cr.iloc[0, 0]
        return (best_feature, corr_best_feature)

    @property
    def is_fitted_(self) -> bool:
        return bool(len(self.pmodels_))

    def fit(self
            , X: pd.DataFrame
            , y: pd.Series
            ) -> PRegressor:

        assert (int(self.garden_cv_score_threshold is None) +
                int(self.garden_cv_score_threshold_multiplier is None) == 1)

        if self.garden_cv_score_threshold is not None:
            assert 0 < self.garden_cv_score_threshold < 1

        if self.garden_cv_score_threshold_multiplier is not None:
            assert 0 < self.garden_cv_score_threshold_multiplier < 1

        self.garden_base_model = update_param_if_supported(
            self.garden_base_model
            ,"random_state"
            ,self.random_state)

        self.base_model_cv_score = CV_Score(
            self.garden_base_model, random_state = self.random_state)


        X, y = self.start_fitting(X, y)

        self.pmodels_ = []
        self.feature_lists_ = []
        self.cv_scores_ = []
        self.log_df_ = None
        omodel_logs = []
        self.fit_cv_score_threshold_ = self.garden_cv_score_threshold
        unprocessed_features = set(X.columns)

        if self.max_features_per_pmodel is not None:
            self.current_max_max_features_per_pmodel = (
                self.max_features_per_pmodel)
        else:
            self.current_max_max_features_per_pmodel = 2*int(len(X) ** 0.5)
            log_message = "max_features_per_omodel was not provided, "
            log_message += f"defaulting to 2*square root of number of samples "
            log_message += f"({self.current_max_max_features_per_pmodel})"
            self.info(log_message)

        recommended_min_features = (self.current_max_max_features_per_pmodel
                                    * self.max_pmodels_per_garden * 3)

        if recommended_min_features > len(X.columns):
            log_message = f"NUMBER OF FEATURES {len(X.columns)} IS TOO LOW, "
            log_message += f"RECOMMENDED MIN # IS {recommended_min_features}"
            self.warning(log_message)

        for i in range(self.max_pmodels_per_garden):
            log_message = f"Attempting to build {i + 1}-th "
            log_message += f"(out of {self.max_pmodels_per_garden}) "
            log_message += f"model in a garden. "
            self.info(log_message)

            X_new = X[sorted(list(unprocessed_features))]

            (model_i, features_i, cv_score_i, log_i) = (
                self.build_an_omodel(X_new, y))

            if self.fit_cv_score_threshold_ is None:
                self.fit_cv_score_threshold_ = (
                        cv_score_i * self.garden_cv_score_threshold_multiplier)

            if cv_score_i < self.fit_cv_score_threshold_:
                log_message = f"OModel # {i + 1} did not reach a minumum cv_score"
                log_message += f" threshold of {self.fit_cv_score_threshold_:.2%}"
                log_message += f" and it will not be included into the garden"
                log_message += f", now stopping model-building process. "
                self.info(log_message)
                break

            self.pmodels_ += [model_i]
            self.feature_lists_ += [sorted(features_i)]
            self.cv_scores_ += [cv_score_i]
            log_i["ModelID"] = i
            omodel_logs += [log_i]
            unprocessed_features -= set(features_i)

        n_models = len(self.pmodels_)
        n_features_used = len(X.columns) - len(unprocessed_features)
        if n_models == 0:
            self.error("No omodels were created for the garden")
        else:
            self.log_df_ = pd.concat(omodel_logs, ignore_index=True)
            assert n_models == self.log_df_["ModelID"].nunique()
            assert n_features_used == (
                self.log_df_[self.log_df_.In_Model]["Feature"].nunique())

        log_message = f"<== {n_models} models were created"
        log_message += f" and included into the garden, alltogether using "
        log_message += f"{n_features_used} features out of {len(X.columns)} "
        log_message += f"available, cv_scores are {self.cv_scores_}."
        self.info(log_message)

        return self

    def predict(self, X
                ) -> pd.Series:

        X = self.start_predicting(X)
        self.last_opredictions_ = []
        n_models = len(self.pmodels_)

        for i in range(n_models):
            self.last_opredictions_ += [
                self.pmodels_[i].predict(X[sorted(self.feature_lists_[i])])]

        ## TODO: refactor mean calculations below
        result = self.last_opredictions_[0]
        for i in range(1, n_models):
            result += self.last_opredictions_[i]
        if n_models > 1:
            result /= n_models

        result = pd.Series(
            data=result, index=X.index, name=self.target_name_)

        return self.finish_predicting(result)

    def build_an_omodel(self
                        , X: pd.DataFrame
                        , y: pd.Series
                        ):
        X = deepcopy(X)
        y = deepcopy(y)
        work_model = clone(self.garden_base_model)
        status_log = pd.DataFrame(
            columns=["Feature", "Correlation", "CV_Score"])

        num_iter = 1
        (first_feature, corr) = self.one_best_feature(X, y)
        remaining_features = list(X.columns)
        remaining_features.remove(first_feature)
        selected_features = [first_feature]
        cv_score = self.base_model_cv_score(X[sorted(selected_features)], y)
        work_model.fit(X[sorted(selected_features)], y)
        predictions = work_model.predict(X[sorted(selected_features)])
        residuals = predictions - y
        status_log = status_log.append(
            {"Feature": first_feature, "Correlation": corr
                , "CV_Score": cv_score}
            , ignore_index=True)

        while (len(remaining_features)
               and corr >= self.garden_feature_cr_threshold
               and num_iter < self.current_max_max_features_per_pmodel):
            num_iter += 1
            (new_feature, corr) = self.one_best_feature(
                X[remaining_features], residuals)
            remaining_features.remove(new_feature)
            selected_features.append(new_feature)
            cv_score = self.base_model_cv_score(
                X[sorted(selected_features)],y)
            work_model = work_model.fit(
                X[sorted(selected_features)], y)
            predictions = work_model.predict(X[sorted(selected_features)])
            residuals = predictions - y
            status_log = status_log.append(
                {"Feature": new_feature, "Correlation": corr
                    , "CV_Score": cv_score}
                , ignore_index=True)

        best_iteration = status_log["CV_Score"].idxmax()
        best_features = sorted(selected_features[:best_iteration + 1])
        best_model = work_model.fit(X[sorted(best_features)], y)
        best_cv_score = status_log.at[best_iteration, "CV_Score"]
        status_log["In_Model"] = (status_log.index <= best_iteration)
        status_log["Rank"] = status_log.index

        log_message = f"<== New OModel has been built. The model has reached "
        log_message += f"the best cv_sore of {best_cv_score:.2%} on its "
        log_message += f"{best_iteration + 1} feature-search iteration "
        log_message += f"(out of {self.current_max_max_features_per_pmodel})."
        self.info(log_message)

        assert (set(best_features) ==
                set(status_log[status_log.In_Model]["Feature"].unique()))

        return best_model, best_features, best_cv_score, status_log


class AmpleGarden(PRegressor):
    is_fitted_flag_: bool

    def __init__(self, *
                , garden_base_model=LinearRegression(normalize=True)
                , garden_feature_cr_threshold: float = 0.08
                , max_features_per_pmodel: Optional[int] = None
                , max_pmodels_per_garden: int = 15
                , garden_cv_score_threshold: Optional[float] = None
                , garden_cv_score_threshold_multiplier: Optional[float] = 0.8

                , min_nan_level: float = 0.05
                , min_cat_size: int = 20
                , max_uniques_per_cat: int = 100
                , positive_arg_num_functions = (power_m1_1p, np.log1p, root_2, power_2)
                , any_arg_num_functions = (passthrough, power_3)
                , imputation_aggr_funcs = (
                    np.min, np.max, percentile50, minmode, maxmode)
                , tme_aggr_funcs = (percentile01
                                   , percentile25
                                   , percentile50
                                   , percentile75
                                   , percentile99
                                   , minmode
                                   , maxmode)
                , split_percentiles = (1, 25, 50, 75, 99)

                , random_state = None
                , **kwargs) -> None:
        super().__init__( **kwargs)
        self.set_params(garden_base_model=garden_base_model
            , garden_feature_cr_threshold=garden_feature_cr_threshold
            , max_features_per_pmodel= max_features_per_pmodel
            , max_pmodels_per_garden= max_pmodels_per_garden
            , garden_cv_score_threshold = garden_cv_score_threshold
            , garden_cv_score_threshold_multiplier = garden_cv_score_threshold_multiplier
            , min_nan_level = min_nan_level
            , min_cat_size = min_cat_size
            , max_uniques_per_cat = max_uniques_per_cat
            , positive_arg_num_functions = positive_arg_num_functions
            , any_arg_num_functions = any_arg_num_functions
            , imputation_aggr_funcs = imputation_aggr_funcs
            , tme_aggr_funcs = tme_aggr_funcs
            , split_percentiles = split_percentiles
            , random_state = random_state
            , **kwargs)

    def set_params(self
            , garden_base_model = None
            , garden_feature_cr_threshold = None
            , max_features_per_pmodel = None
            , max_pmodels_per_garden = None
            , garden_cv_score_threshold = None
            , garden_cv_score_threshold_multiplier = None
            , min_nan_level = None
            , min_cat_size = None
            , max_uniques_per_cat = None
            , positive_arg_num_functions = None
            , any_arg_num_functions = None
            , imputation_aggr_funcs = None
            , tme_aggr_funcs = None
            , split_percentiles = None
            , random_state = None
            , **kwargs) -> PRegressor:
        self.is_fitted_flag_ = False

        self.random_state = random_state

        self.feature_shower = FeatureShower(
            min_nan_level=min_nan_level
            , min_cat_size=min_cat_size
            , max_uniques_per_cat=max_uniques_per_cat
            , positive_arg_num_functions=positive_arg_num_functions
            , any_arg_num_functions=any_arg_num_functions
            , imputation_aggr_funcs=imputation_aggr_funcs
            , tme_aggr_funcs=tme_aggr_funcs
            , split_percentiles=split_percentiles
            , random_state=random_state)

        self.simple_garden = SimpleGarden(
            garden_base_model=garden_base_model
            , garden_feature_cr_threshold=garden_feature_cr_threshold
            , max_features_per_pmodel=max_features_per_pmodel
            , max_pmodels_per_garden=max_pmodels_per_garden
            , garden_cv_score_threshold=garden_cv_score_threshold
            , garden_cv_score_threshold_multiplier=garden_cv_score_threshold_multiplier
            , random_state=random_state)

        return self

    def get_params(self, deep: bool = False) -> Dict[str, Any]:
        fs_params = self.feature_shower.get_params(deep)
        sg_params = self.simple_garden.get_params(deep)
        params = {**fs_params, **sg_params, "random_state":self.random_state}
        return params

    @property
    def is_fitted_(self):
        return self.is_fitted_flag_

    @property
    def input_columns_(self) -> List[str]:
        return self.feature_shower.input_columns_

    @property
    def input_can_have_nans(self) -> bool:
        return True

    @property
    def output_can_have_nans(self) -> bool:
        return False

    def fit(self, X, y):
        X, y = self.start_fitting(X, y)
        X_new = self.feature_shower.fit_transform(X,y)
        self.simple_garden.fit(X_new,y)
        self.is_fitted_flag_ = True
        return self

    def predict(self, X):
        X = self.start_predicting(X)
        X_new = self.feature_shower.transform(X)
        result = self.simple_garden.predict(X_new)
        return self.finish_predicting(result)



class BaggingStabilizer(PRegressor):
    is_fitted_flag_: bool
    stabilizer_n_splits:int
    stabilizer_n_repeats:int
    base_model:PRegressor
    stabilizer_percentile:int
    stabilizer_add_full_model:bool
    rkf:RepeatedKFold
    models_: Optional[List[PRegressor]]
    model_scores_:Optional[List[float]]
    rejected_model_scores_:Optional[List[float]]
    cv_score_: Optional[float]
    inp_clmns_:Optional[List[str]]

    def __init__(self
                 , base_model = AmpleGarden()
                 , stabilizer_n_splits:int=5
                 , stabilizer_n_repeats:int=4
                 , stabilizer_percentile:int=50
                 , stabilizer_add_full_model:bool = False
                 , random_state = None
                 , *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_params(
            base_model=base_model
            , stabilizer_n_splits=stabilizer_n_splits
            , stabilizer_n_repeats=stabilizer_n_repeats
            , stabilizer_percentile = stabilizer_percentile
            , stabilizer_add_full_model = stabilizer_add_full_model
            , random_state = random_state)

    def set_params(self
            ,base_model=None
            , stabilizer_n_splits:int=None
            , stabilizer_n_repeats:int=None
            , stabilizer_percentile = None
            , stabilizer_add_full_model = None
            , random_state=None
            , deep: bool = False
            ,**kwargs) -> PRegressor:
        self.base_model = base_model
        self.stabilizer_n_splits = stabilizer_n_splits
        self.stabilizer_n_repeats = stabilizer_n_repeats
        self.stabilizer_percentile = stabilizer_percentile
        self.stabilizer_add_full_model = stabilizer_add_full_model
        self.is_fitted_flag_ = False
        self.models = None
        self.model_scores_ = None
        self.rejected_model_scores_ = None
        self.cv_score_ = None
        self.inp_clmns_ = None
        self.random_state = random_state
        return self

    def get_params(self, deep: bool = False) -> Dict[str, Any]:
        params = dict(base_model = self.base_model
            , n_splits = self.stabilizer_n_splits
            , n_repeats = self.stabilizer_n_repeats
            , percentile = self.stabilizer_percentile
            , stabilizer_add_full_model = self.stabilizer_add_full_model
            , random_state = self.random_state)
        return params

    @property
    def is_fitted_(self):
        return self.is_fitted_flag_

    @property
    def input_columns_(self) -> List[str]:
        return self.inp_clmns_

    @property
    def input_can_have_nans(self) -> bool:
        return self.base_model.input_can_have_nans

    @property
    def output_can_have_nans(self) -> bool:
        return self.base_model.output_can_have_nans

    def fit(self, X, y):
        assert self.stabilizer_n_splits in range(2, 100)
        assert self.stabilizer_n_repeats in range(2, 100)
        assert self.stabilizer_percentile in range(10, 91)

        self.base_model = update_param_if_supported(
            self.base_model, "random_state", self.random_state)

        self.rkf = RepeatedKFold(
            n_splits=self.stabilizer_n_splits
            , n_repeats=self.stabilizer_n_repeats
            , random_state=self.random_state)

        X, y = self.start_fitting(X, y)
        cv_results = cross_validate(self.base_model
            ,X
            ,y
            ,scoring = "r2"
            ,cv = self.rkf
            ,return_estimator = True
            ,n_jobs=-1)

        score_threshold = np.nanpercentile(
            cv_results["test_score"], self.stabilizer_percentile)
        n_scores = len(cv_results["test_score"])
        self.model_scores_ = []
        self.models_ = []
        self.rejected_model_scores_ = []

        for i in range(n_scores):
            if cv_results["test_score"][i] >= score_threshold:
                self.model_scores_ += [cv_results["test_score"][i]]
                self.models_ += [cv_results["estimator"][i]]
            else:
                self.rejected_model_scores_ += [cv_results["test_score"][i]]

        self.cv_score_ = score_threshold

        if self.stabilizer_add_full_model:
            self.models_ += [self.base_model.fit(X,y)]
            self.model_scores_ += [self.cv_score_]

        input_columns = set()
        for m in self.models_:
            input_columns |= set(m.input_columns_)
        self.inp_clmns_ = sorted(list(input_columns))


        message_log = f"<== Fitting process has finished, expected CV_Score"
        message_log += f" is {self.cv_score_}. "
        message_log += f"{len(self.models_)} models have been included into "
        message_log += f"the final asembly, {len(self.rejected_model_scores_)} "
        message_log += f" models have been rejected. Included models have the "
        message_log += f" following scores: {sorted(self.model_scores_)}, "
        message_log += f" rejected scores are "
        message_log += f"{sorted(self.rejected_model_scores_)}."
        self.info(message_log)

        assert min(self.model_scores_) >= self.cv_score_
        assert max(self.rejected_model_scores_) <= self.cv_score_

        self.is_fitted_flag_ = True

        return self

    def predict(self, X):
        X = self.start_predicting(X)

        self.last_opredictions_ = []
        n_models = len(self.models_)

        for i in range(n_models):
            self.last_opredictions_ += [
                self.models_[i].predict(X)]

        result = self.last_opredictions_[0]
        for i in range(1, n_models):
            result += self.last_opredictions_[i]
        if n_models > 1:
            result /= n_models

        if not isinstance(result, pd.Series):
            result = pd.Series(
                data=result, index=X.index, name=self.target_name_)

        return self.finish_predicting(result)


class MagicGarden(PRegressor):
    is_fitted_flag_: bool

    def __init__(self, *
                , garden_base_model= LinearRegression(normalize=True)
                , garden_feature_cr_threshold: float = 0.07
                , max_features_per_pmodel: Optional[int] = None
                , max_pmodels_per_garden: int = 15
                , garden_cv_score_threshold: Optional[float] = None
                , garden_cv_score_threshold_multiplier: Optional[float] = 0.8

                , min_nan_level: float = 0.05
                , min_cat_size: int = 20
                , max_uniques_per_cat: int = 100
                , positive_arg_num_functions = (power_m1_1p, np.log1p, root_2, power_2)
                , any_arg_num_functions = (passthrough, power_3)
                , imputation_aggr_funcs = (
                    np.min, np.max, percentile50, minmode, maxmode)
                , tme_aggr_funcs = (percentile01
                                   , percentile25
                                   , percentile50
                                   , percentile75
                                   , percentile99
                                   , minmode
                                   , maxmode)
                , split_percentiles = (1, 25, 50, 75, 99)

                , stabilizer_n_splits: int = 5
                , stabilizer_n_repeats: int = 4
                , stabilizer_percentile: int = 50
                , stabilizer_add_full_model: bool = False

                , random_state = None
                , **kwargs) -> None:
        super().__init__( **kwargs)
        self.set_params(garden_base_model=garden_base_model
            , garden_feature_cr_threshold=garden_feature_cr_threshold
            , max_features_per_pmodel= max_features_per_pmodel
            , max_pmodels_per_garden= max_pmodels_per_garden
            , garden_cv_score_threshold = garden_cv_score_threshold
            , garden_cv_score_threshold_multiplier = garden_cv_score_threshold_multiplier
            , min_nan_level = min_nan_level
            , min_cat_size = min_cat_size
            , max_uniques_per_cat = max_uniques_per_cat
            , positive_arg_num_functions = positive_arg_num_functions
            , any_arg_num_functions = any_arg_num_functions
            , imputation_aggr_funcs = imputation_aggr_funcs
            , tme_aggr_funcs = tme_aggr_funcs
            , split_percentiles = split_percentiles
            , stabilizer_n_splits = stabilizer_n_splits
            , stabilizer_n_repeats = stabilizer_n_repeats
            , stabilizer_percentile = stabilizer_percentile
            , stabilizer_add_full_model = stabilizer_add_full_model
            , random_state = random_state
            , **kwargs)

    def set_params(self
            , garden_base_model = None
            , garden_feature_cr_threshold = None
            , max_features_per_pmodel = None
            , max_pmodels_per_garden = None
            , garden_cv_score_threshold = None
            , garden_cv_score_threshold_multiplier = None
            , min_nan_level = None
            , min_cat_size = None
            , max_uniques_per_cat = None
            , positive_arg_num_functions = None
            , any_arg_num_functions = None
            , imputation_aggr_funcs = None
            , tme_aggr_funcs = None
            , split_percentiles = None
            , stabilizer_n_splits: int = None
            , stabilizer_n_repeats: int = None
            , stabilizer_percentile=None
            , stabilizer_add_full_model=None
            , random_state = None
            , **kwargs) -> PRegressor:
        self.is_fitted_flag_ = False

        self.random_state = random_state

        self.ample_garden = AmpleGarden(
            garden_base_model=garden_base_model
            , garden_feature_cr_threshold=garden_feature_cr_threshold
            , max_features_per_pmodel=max_features_per_pmodel
            , max_pmodels_per_garden=max_pmodels_per_garden
            , garden_cv_score_threshold=garden_cv_score_threshold
            , garden_cv_score_threshold_multiplier=garden_cv_score_threshold_multiplier
            , min_nan_level=min_nan_level
            , min_cat_size=min_cat_size
            , max_uniques_per_cat=max_uniques_per_cat
            , positive_arg_num_functions=positive_arg_num_functions
            , any_arg_num_functions=any_arg_num_functions
            , imputation_aggr_funcs=imputation_aggr_funcs
            , tme_aggr_funcs=tme_aggr_funcs
            , split_percentiles=split_percentiles
            , random_state=random_state)

        self.bagging_stabilizer = BaggingStabilizer(
            base_model = self.ample_garden
            , stabilizer_n_splits = stabilizer_n_splits
            , stabilizer_n_repeats = stabilizer_n_repeats
            , stabilizer_percentile = stabilizer_percentile
            , stabilizer_add_full_model = stabilizer_add_full_model
            , random_state=random_state)

        return self

    def get_params(self, deep: bool = False) -> Dict[str, Any]:
        ag_params = self.ample_garden.get_params(deep)
        st_params = self.bagging_stabilizer.get_params(deep)
        params = {**ag_params, **st_params, "random_state":self.random_state}
        self.info(params)
        return params

    @property
    def is_fitted_(self):
        return self.is_fitted_flag_

    @property
    def input_columns_(self) -> List[str]:
        return self.bagging_stabilizer.input_columns_

    @property
    def input_can_have_nans(self) -> bool:
        return True

    @property
    def output_can_have_nans(self) -> bool:
        return False

    def fit(self, X, y):
        X, y = self.start_fitting(X, y)
        X_new = self.bagging_stabilizer.fit(X,y)
        self.is_fitted_flag_ = True
        return self

    def predict(self, X):
        X = self.start_predicting(X)
        result = self.bagging_stabilizer.predict(X)
        return self.finish_predicting(result)

