import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, GridSearchCV

from Pythagoras.logging import *
from Pythagoras.caching import *
from Pythagoras.util import *
from Pythagoras.base import *
from Pythagoras.global_objects import *


class MapperSmokeTester(LoggableObject):
    """Basic smoke-test runner for P.Mappers and SKLearn Estimators"""
    def __init__(self
                 , mapper_to_test
                 , splitting = 7
                 , scoring = "r2"
                 , logging_level = logging.WARNING):
        super().__init__(logging_level = logging_level)
        self.mapper_to_test = clone(mapper_to_test)
        self.splitting = splitting
        self.scoring = scoring
        for dataset in [Boston, California]:
            self.run_test(dataset)

    def run_test(self, dataset = Boston):
        log_message = "==> Starting executing a smoke-test for "
        log_message += f"{self.mapper_to_test.__class__.__name__} with "
        log_message += f"cv={self.splitting} "
        log_message += f"and scoring={self.scoring}. Sample "
        log_message += f"dataset is named {NeatStr.object_names(dataset)} "
        log_message += f"and its X's shape is {dataset.X.shape}."
        self.info(log_message)

        cv_scores = cross_val_score(
            self.mapper_to_test
            , dataset.X
            , dataset.y
            , cv=self.splitting
            , scoring=self.scoring)
        log_message = "<== Smoke-test has finished. Min, median and max "
        log_message += f"values for CV-score are: "
        log_message += f"{min(cv_scores)}, "
        log_message += f"{median(cv_scores)}, "
        log_message += f"{max(cv_scores)}."
        self.info(log_message)


class MapperParamGridAnalyser(LoggableObject):
    """Grid search analyser for P.Mappers and SKLearn Estimators"""
    def __init__(self
                 , mapper_to_test
                 , param_grid = None
                 , splitting = 7
                 , scoring = "r2"
                 , logging_level = logging.WARNING):
        super().__init__(logging_level = logging_level)
        self.mapper_to_test = clone(mapper_to_test)
        self.splitting = splitting
        self.scoring = scoring
        self.param_grid = param_grid
        self.run_test()

    def run_test(self, dataset = California):
        log_message = "==> Starting executing grid-search analysis for "
        log_message += f"{self.mapper_to_test.__class__.__name__} with "
        log_message += f"cv={self.splitting}, "
        log_message += f"scoring={self.scoring} and "
        log_message += f"param_grid={self.param_grid}. Sample "
        log_message += f"dataset is named {NeatStr.object_names(dataset)} "
        log_message += f"and its X's shape is {dataset.X.shape}."
        self.info(log_message)

        gs_cv = GridSearchCV(
            estimator = self.mapper_to_test
            ,param_grid = self.param_grid
            ,scoring = self.scoring
            , cv = self.splitting
            , refit = False)

        gs_cv.fit(dataset.X, dataset.y)
        self.log_df = pd.DataFrame(gs_cv.cv_results_)
        split_column_names = [c for c in self.log_df.columns if c.startswith("split")]
        param_column_names = [c for c in self.log_df.columns if
                              c.startswith("param")]

        self.summary_df = deepcopy(self.log_df[param_column_names])
        self.summary_df["min_score"] = self.log_df[
            split_column_names].min(axis="columns")
        self.summary_df["mean_score"] = self.log_df[
            split_column_names].mean(axis="columns")
        self.summary_df["median_score"] = self.log_df[
            split_column_names].median(axis="columns")
        self.summary_df["max_score"] = self.log_df[
            split_column_names].max(axis="columns")


        log_message = "<== Analysis has finished with "
        log_message += f"the best score of {gs_cv.best_score_}, and "
        log_message += f"best params {gs_cv.best_params_}."
        self.info(log_message)

