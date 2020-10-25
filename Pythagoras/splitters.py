import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from numpy import mean, median
import numpy as np
from sklearn import clone
from sklearn.model_selection import KFold, StratifiedKFold

from Pythagoras.util import *
from Pythagoras.logging import *
from Pythagoras.caching import *

class AdaptiveKFold:
    def __init__(self
                 , *
                 , n_splits=5
                 , shuffle=False
                 , random_state=None
                 , max_bins = 20) -> None:
        self.n_splits = n_splits
        self.shuffle = shuffle
        self.random_state = random_state
        self._nested_splitter = None
        self.max_bins = max_bins

    def split(self, X, y=None, *, groups=None):
        if self._nested_splitter is None:
            self._nested_splitter = KFold(
                n_splits=self.n_splits
                , shuffle=self.shuffle
                , random_state=self.random_state)

            # if isinstance(y,np.ndarray) and y.ndim == 1: #TODO: check
            #     (_,counts) = np.unique(y,return_counts = True)
            #     if len(counts) <= self.max_bins and min(counts) <= self.n_splits:
            #         self._nested_splitter = StratifiedKFold(
            #             n_splits=self.n_splits
            #             , shuffle=self.shuffle
            #             , random_state=self.random_state)
            #         # TODO: Check if y needs to be converted

        return self._nested_splitter.split(X,y,groups)

    def get_n_splits(self, X=None, y=None, groups=None) -> int:
        return self.n_splits

    def __repr__(self):

        if self._nested_splitter is None:
            repr_str = f"Nested splitter is not initialized, "
            repr_str += f"{self.n_splits=}, {self.shuffle=}, "
            repr_str += f"{self.max_bins=}, {self.random_state=}"
        else:
            repr_str = repr(self._nested_splitter)

        repr_str = f"{self.__class__.__name__}({repr_str})"

        return repr_str


