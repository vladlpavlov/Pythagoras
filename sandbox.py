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

nani = NaN_Inducer()
a = nani.fit_transform(Boston.X, Boston.y)
b = nani.transform(Boston.X)

ni = NumericImputer()
aa = ni.fit_transform(a, Boston.y)
bb = ni.transform(b)

d = Deduper()
a_d = d.fit_transform(aa,Boston.y)
b_d = d.transform(bb)

print()