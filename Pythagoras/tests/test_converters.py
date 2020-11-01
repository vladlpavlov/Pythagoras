import pytest
from sklearn.linear_model import LogisticRegressionCV

from Pythagoras import *
import time
import os
import numpy as np

class TestConverters:
    def test_regression(self):
        regressors = [Ridge(), LGBMRegressor(), CatBoostRegressor()]
        dataset = Boston
        for r in regressors:
            r=get_mapper(r, leakproof=True)
            r.fit(dataset.X, dataset.Y)
            z = r.map(dataset.X)
            r.warning(f"Score for testing {get_typeid(r)} "
                + f"on {dataset.name} "
                +  f"is {r.get_scorer()(r,dataset.X, dataset.Y)}")

    def test_classifiers(self):
        classifiers = [LogisticRegression(max_iter = 250), LGBMClassifier(), CatBoostClassifier()]
        dataset = Iris
        for c in classifiers:
            c=get_mapper(c, leakproof=True)
            c.fit(dataset.X, dataset.Y)
            z = c.map(dataset.X)
            c.warning(f"Score for testing {get_typeid(c)} "
                + f"on {dataset.name} "
                +  f"is {c.get_scorer()(c,dataset.X, dataset.Y)}")