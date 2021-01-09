from random import shuffle

import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.metrics import get_scorer
from sklearn.model_selection import cross_validate, ParameterGrid

from Pythagoras.misc_utils import *
from Pythagoras.base import *
from Pythagoras.loggers import *
from Pythagoras.feature_engineering import *
from Pythagoras.caching import *
from Pythagoras.global_objects import *


