import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from numpy import mean, median
from sklearn import clone
from sklearn.base import BaseEstimator
from sklearn.metrics import get_scorer
from sklearn.metrics._scorer import _BaseScorer
from sklearn.model_selection import BaseCrossValidator

from Pythagoras.misc_utils import *
from Pythagoras.logging import *
from Pythagoras.caching import *
from Pythagoras.splitters import *
from Pythagoras.filters import *


class NotKnownType:
    """ Singleton for 'NotKnown' constant """

    not_known_single_instance = None

    def __new__(cls):
        if cls.not_known_single_instance is None:
            cls.not_known_single_instance = super().__new__(cls)
        return cls.not_known_single_instance

NotKnown = NotKnownType()