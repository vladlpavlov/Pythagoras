from sklearn.datasets import load_boston, fetch_california_housing
from Pythagoras import *


class DemoDB:
    def __init__(self, db: str):
        if db == "Boston":
            load_function = load_boston
            target_name = "MEDV"
        elif db == "California":
            load_function = fetch_california_housing
            target_name = "MedHouseVal"
        else:
            assert False

        dt = load_function()
        self.X = pd.DataFrame(data=dt.data, columns=dt.feature_names)
        self.y = pd.Series(data=dt.target, name=target_name)
        self.description = dt.DESCR

    def __str__(self):
        return self.description

    def __repr__(self):
        return self.description

Boston = DemoDB("Boston")
California = DemoDB("California")


class NewMagicalGarden(PRegressor):
    pass


class NewMagicalGarden(PRegressor):
    is_fitted_flag_: bool
    columns_: List[str]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set_params()

    def set_params(self, deep: bool = False) -> NewMagicalGarden:
        self.nan_inducer = NaN_Inducer()
        self.dummies_maker = DummiesMaker()
        self.numeric_func_transformer = NumericFuncTransformer()
        self.numeric_imputer = NumericImputer()
        self.target_multi_encoder = TargetMultiEncoder()
        self.deduper = Deduper()
        self.d_garden = DeterministicGarden()
        self.is_fitted_flag_ = False
        return self

    def get_params(self, deep: bool = False) -> Dict[str, Any]:
        return {}

    @property
    def is_fitted_(self):
        return self.is_fitted_flag_

    @property
    def input_columns_(self) -> List[str]:
        return sorted(self.columns_)

    @property
    def input_can_have_nans(self) -> bool:
        return True

    @property
    def output_can_have_nans(self) -> bool:
        return False

    def fit(self, X, y):
        X, y = self.start_fitting(X, y)
        self.columns_ = sorted(X.columns)
        X_with_NaNs = self.nan_inducer.fit_transform(X, y)

        X_numeric_tr = self.numeric_func_transformer.fit_transform(
            X_with_NaNs, y)

        X_numeric_no_NaNs = self.numeric_imputer.fit_transform(X_numeric_tr, y)

        X_dummies = self.dummies_maker.fit_transform(X_with_NaNs,y)
        for c in X_dummies:
            X_dummies[c] =1

        X_target_encoded_cats = self.target_multi_encoder.fit_transform(
            X_with_NaNs, y)

        X_full = pd.concat(
            [X_numeric_no_NaNs, X_target_encoded_cats, X_dummies], axis=1)


        X_final = self.deduper.fit_transform(X_full, y)

        self.d_garden.fit(X_final, y)
        self.is_fitted_flag_ = True
        return self

    def predict(self, X):
        X = self.start_predicting(X)
        X_with_NaNs = self.nan_inducer.transform(X)

        X_numeric_tr = self.numeric_func_transformer.transform(X_with_NaNs)

        X_numeric_no_NaNs = self.numeric_imputer.transform(X_numeric_tr)

        X_dummies = self.dummies_maker.transform(X_with_NaNs)
        for c in X_dummies:
            X_dummies[c] =1

        X_target_encoded_cats = self.target_multi_encoder.transform(
            X_with_NaNs)
        X_full = pd.concat(
            [X_numeric_no_NaNs, X_target_encoded_cats,X_dummies], axis=1)

        X_final = self.deduper.transform(X_full)
        result = self.d_garden.predict(X_final)
        return self.finish_predicting(result)


new_mg = NewMagicalGarden()


ncv_score = CV_Score(new_mg)
print(ncv_score(Boston.X, Boston.y))
print(ncv_score.scores_)



#
# nani = NaN_Inducer()
# a_nans = nani.fit_transform(Boston.X, Boston.y)
# b_nans = nani.transform(Boston.X)
#
# nft = NumericFuncTransformer()
# a = nft.fit_transform(a_nans,Boston.y)
#
# b = nft.transform(b_nans)
#
# ni = NumericImputer()
# aa = ni.fit_transform(a, Boston.y)
# bb = ni.transform(b)
#
# d = Deduper()
# a_d = d.fit_transform(aa,Boston.y)
# b_d = d.transform(bb)

print()