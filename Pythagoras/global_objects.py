from Pythagoras.misc_utils import *
from Pythagoras.loggers import *
from Pythagoras.caching import *


class DemoDB:
    """ An OOP wrapper for popular SKLearn datasets"""
    def __init__(self, db_name: str):
        self.name = db_name
        if db_name == "Boston":
            load_function = load_boston
            target_name = "MEDV"
        elif db_name == "California":
            load_function = fetch_california_housing
            target_name = "MedHouseVal"
        elif db_name == "Iris":
            load_function = load_iris
            target_name = "IrisClass"
        else:
            assert False

        dt = load_function()
        self.X = pd.DataFrame(data=dt.data, columns=dt.feature_names)
        self.Y = pd.Series(data=dt.target, name=target_name)
        self.y = self.Y
        self.description = dt.DESCR

    def __str__(self):
        return self.description

    def __repr__(self):
        return self.description

# Boston = DemoDB("Boston")
# California = DemoDB("California")
# Iris = DemoDB("Iris")