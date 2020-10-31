import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score, GridSearchCV

from Pythagoras.logging import *
from Pythagoras.caching import *
from Pythagoras.misc_utils import *
from Pythagoras.base import *
from Pythagoras.global_objects import *

class MapperParamGridAnalyser(LoggableObject):
    """Grid search analyser for P.Mappers"""
    def __init__(self
                 , mapper_to_test
                 , param_grid = None
                 , splitting = 5
                 , n_repeats:int = 7
                 , datasets = None
                 , scoring = None
                 , logging_level:Union[int, str,None] = logging.DEBUG):
        super().__init__(
            logging_level = logging_level
            ,reveal_calling_method=True
            ,root_logger_name="Pythagoras")

        self.mapper_to_test = clone(mapper_to_test)
        self.n_repeats = n_repeats

        if splitting is None:
            self.splitting = self.mapper_to_test.splitting
        else:
            self.splitting = splitting

        if isinstance(self.splitting, int):
            self.splitting = AdaptiveKFold(n_splits=self.splitting)

        if scoring is None:
            self.scoring = self.mapper_to_test.scoring
        else:
            self.scoring = scoring

        if param_grid is None:
            self.param_grid = {}
        else:
            self.param_grid = param_grid

        if datasets is None:
            self.datasets = [Boston, California]
        else:
            self.datasets = datasets

        self.log_df = self.run_all_testsets()
        self.summary_df = self.build_summary_df(self.log_df)

    def compose_summary_message(self, data_df) -> str:

        split_column_names = [
            c for c in data_df.columns if c.startswith("split")]

        min_score = data_df[split_column_names].min().min()
        mean_score = data_df[split_column_names].mean().mean()
        max_score = data_df[split_column_names].max().max()

        message = "analysis has finished with "
        message += f"the following min/mean/max scores: "
        message += f"{min_score} / {mean_score} / {max_score}."

        return message

    def build_summary_df(self, data_df) -> pd.DataFrame:
        split_column_names = [
            c for c in data_df.columns if c.startswith("split")]
        param_column_names = [
            c for c in data_df.columns if c.startswith("param")]
        summary_df = deepcopy(data_df[param_column_names])
        summary_df["dataset"] = data_df["dataset"]

        summary_df["min_score"] = data_df[
            split_column_names].min(axis="columns")
        summary_df["mean_score"] = data_df[
            split_column_names].mean(axis="columns")
        summary_df["median_score"] = data_df[
            split_column_names].median(axis="columns")
        summary_df["max_score"] = data_df[
            split_column_names].max(axis="columns")

        return summary_df


    def run_single_testset(self
                           , dataset
                           , id_str):
        log_message = "==> Starting executing grid-search analysis "
        log_message += f"with dataset={dataset.name} id_str={id_str} ."
        self.info(log_message)

        gs_cv = GridSearchCV(
            estimator = self.mapper_to_test
            ,param_grid = self.param_grid
            ,scoring = self.scoring
            ,cv = self.splitting
            ,refit = False)

        gs_cv.fit(dataset.X, dataset.y)
        log_df = pd.DataFrame(gs_cv.cv_results_)

        split_column_names = [
            c for c in log_df.columns if c.startswith("split")]
        split_column_names = [
            c for c in split_column_names if c.endswith("_test_score")]
        split_column_converter = {
            c: c + "_" + id_str for c in split_column_names}

        param_column_names = [
            c for c in log_df.columns if c.startswith("param")]

        log_df.rename(columns=split_column_converter, inplace = True)
        split_column_names = [
            split_column_converter[c] for c in split_column_converter]

        splits_df = log_df[["params"] + split_column_names]
        params_df = log_df[param_column_names]

        log_message = f"<== dataset={dataset.name}, id_str={id_str}: "
        log_message += self.compose_summary_message(splits_df)
        self.info(log_message)

        num_nans = splits_df.isna().sum().sum() + params_df.isna().sum().sum()
        if num_nans:
            error_message = f"NaNs were detected in GridSearchCV results."
            self.error(error_message)

        return deepcopy(splits_df), deepcopy(params_df)

    def run_dataset_testsets(self, dataset):
        all_split_dfs = []
        assert self.n_repeats >= 1

        if self.n_repeats >= 2:
            log_message = "==> Starting executing grid-search analysis "
            log_message += f"for dataset={dataset.name} ."
            self.info(log_message)

        for n in range(self.n_repeats):
            id_str = f"iter_{n+1}_of_{self.n_repeats}"
            (split_df, params_df) = self.run_single_testset(
                dataset=dataset, id_str=id_str)
            split_df["params"] = split_df["params"].astype(str)
            split_df.set_index("params", inplace=True)
            all_split_dfs += [split_df]
        if len(all_split_dfs) <= 1:
            final_split_df = all_split_dfs[0]
        else:
            final_split_df = all_split_dfs[0].join(all_split_dfs[1:])

        params_df["params"]=params_df["params"].astype(str)
        params_df.set_index("params", inplace=True)

        result_df = final_split_df.join(params_df)
        result_df.index.name = "index_params"
        result_df["params"] = result_df.index

        if self.n_repeats >= 2:
            log_message = f"<== Dataset={dataset.name}: "
            log_message += self.compose_summary_message(result_df)
            self.info(log_message)

        return result_df

    def run_all_testsets(self):
        all_dbs_dfs = []

        if len(self.datasets) >= 2:
            datasets_names = [db.name for db in self.datasets]
            log_message = "==> Starting executing grid-search analysis "
            log_message += f"with the following datasets: "
            log_message += f"{datasets_names} ."
            self.info(log_message)

        for dts in self.datasets:
            one_db_df = self.run_dataset_testsets(dts)
            one_db_df["dataset"] = dts.name
            all_dbs_dfs += [one_db_df]

        result_df = pd.concat(
            all_dbs_dfs, axis="index",ignore_index=True)

        if len(self.datasets) >= 2:
            log_message = f"<== All datasets {datasets_names}: "
            log_message += self.compose_summary_message(result_df)
            self.info(log_message)

        num_nans = result_df.isna().sum().sum()
        if num_nans:
            error_message = f"Final analysis report contains {num_nans} NaN-s"
            self.error(error_message)

        return result_df

def smoke_test_a_mapper(mapper_to_test):
    test_results = MapperParamGridAnalyser(
        mapper_to_test=mapper_to_test
        , splitting=5
        , n_repeats=10
        , datasets=[California]
        , logging_level="INFO")