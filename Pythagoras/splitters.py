import pandas as pd
from copy import deepcopy
from typing import Optional, Set, List, Dict

from numpy import mean, median
import numpy as np
from sklearn import clone
from sklearn.model_selection import KFold, StratifiedKFold, ShuffleSplit, StratifiedShuffleSplit

from Pythagoras.misc_utils import *
from Pythagoras.not_known import *
from Pythagoras.loggers import *
from Pythagoras.caching import *

class AdaptiveSplitter(LoggableObject):
    def __init__(self
                 , *
                 , n_splits = 10
                 , random_state=None
                 , max_bins = 20
                 , root_logger_name:str = "Pythagoras"
                 , logging_level = "DEBUG"
                 )-> None:
        super().__init__(root_logger_name=root_logger_name, logging_level=logging_level)
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
                 , max_bins = 20
                 , root_logger_name:str = "Pythagoras"
                 , logging_level = "DEBUG"
                 ) -> None:
        super().__init__(
            n_splits=n_splits
            , random_state=random_state
            , max_bins=max_bins
            , root_logger_name = root_logger_name
            , logging_level = logging_level)
        self.shuffle = shuffle

    def split(self, X, y=None, groups=None):
        if self._nested_splitter is None:
            self._nested_splitter = KFold(
                n_splits=self.n_splits
                , shuffle=self.shuffle
                , random_state=self.random_state)

            values = []
            counts = []
            strat_flag = False

            if y.ndim==1 or (y.ndim==2 and y.shape[1]==1):
                (values,counts) = np.unique(y,return_counts = True)
                if len(counts) <= self.max_bins and min(counts) >= self.n_splits:
                    strat_flag = True
                    self._nested_splitter = StratifiedKFold(
                        n_splits=self.n_splits
                        , shuffle=self.shuffle
                        , random_state=self.random_state)

            log_message = f"Created a nested {str(self._nested_splitter)}. "
            if strat_flag:
                log_message += f"y.shape={y.shape}, values={values}, counts={counts}."
            self.debug(log_message)

        return self._nested_splitter.split(X,y,groups)


class AdaptiveShuffleSplit(AdaptiveSplitter):
    def __init__(self
                 , *
                 , n_splits=5
                 , train_size = None
                 , test_size = None
                 , random_state=None
                 , max_bins = 20
                 , root_logger_name: str = "Pythagoras"
                 , logging_level="DEBUG"
                 ) -> None:
        super().__init__(
            n_splits=n_splits
            , random_state=random_state
            , max_bins=max_bins
            , root_logger_name=root_logger_name
            , logging_level=logging_level)
        self.train_size = train_size
        self.test_size = test_size

    def split(self, X, y=None, groups=None):
        if self._nested_splitter is None:
            self._nested_splitter = ShuffleSplit(
                n_splits=self.n_splits
                , train_size=self.train_size
                , test_size =self.test_size
                , random_state=self.random_state)

            values = []
            counts = []
            strat_flag = False

            if y.ndim == 1 or (y.ndim == 2 and y.shape[1] == 1):
                (values, counts) = np.unique(y, return_counts=True)
                if len(counts) <= self.max_bins and min(counts) >= self.n_splits:
                    strat_flag = True
                    self._nested_splitter = StratifiedShuffleSplit(
                        n_splits=self.n_splits
                        , random_state=self.random_state)

            log_message = f"Created nested {str(self._nested_splitter)}. "
            if strat_flag:
                log_message += f"y.shape={y.shape}, values={values}, counts={counts}."
            self.debug(log_message)

        return  self._nested_splitter.split(X,y,groups)
