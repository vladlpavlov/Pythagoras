import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from numpy import mean, median
import numpy as np
from sklearn import clone
from sklearn.model_selection import KFold, StratifiedKFold, ShuffleSplit

from Pythagoras.util import *
from Pythagoras.logging import *
from Pythagoras.caching import *

class AdaptiveSplitter:
    def __init__(self
                 , *
                 , n_splits = 10
                 , random_state=None
                 , max_bins = 20
                 )-> None:
        self.random_state = random_state
        self.n_splits = n_splits
        self._nested_splitter = None
        self.max_bins = max_bins

    def get_n_splits(self, X=None, y=None, groups=None) -> int:
        return self.n_splits

    def __repr__(self):
        repr_str = f"{self.__class__.__name__}( "
        if self._nested_splitter is None:
            repr_str += f"Nested splitter is not initialized, "
            attrs = [a for a in dir(self) if not a.startswith("_")]
            attrs = [a for a in attrs if not callable(getattr(self,a))]
            attrs = [a + "=" + str(getattr(self,a)) for a in attrs]
            repr_str += ", ".join(attrs)
        else:
            repr_str += repr(self._nested_splitter)
        repr_str += " )"
        return repr_str


class AdaptiveKFold(AdaptiveSplitter):
    def __init__(self
                 , *
                 , n_splits=5
                 , shuffle=True
                 , random_state=None
                 , max_bins = 20) -> None:
        super().__init__(
            n_splits=n_splits
            , random_state=random_state
            , max_bins=max_bins)
        self.shuffle = shuffle

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


class AdaptiveShuffleSplit(AdaptiveSplitter):
    def __init__(self
                 , *
                 , n_splits=5
                 , train_size = None
                 , test_size = None
                 , random_state=None
                 , max_bins = 20) -> None:
        super().__init__(
            n_splits=n_splits
            , random_state=random_state
            , max_bins=max_bins)
        self.train_size = train_size
        self.test_size = test_size

    def split(self, X, y=None, *, groups=None):
        if self._nested_splitter is None:
            self._nested_splitter = ShuffleSplit(
                n_splits=self.n_splits
                , train_size=self.train_size
                , test_size =self.test_size
                , random_state=self.random_state)

        return self._nested_splitter.split(X,y,groups)
