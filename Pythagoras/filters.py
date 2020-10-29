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
from Pythagoras.not_known import *
from Pythagoras.logging import *
from Pythagoras.caching import *
from Pythagoras.splitters import *


class ColumnFilter:
    def __init__(self, names:Optional[List[str]]=None) -> None:
        super().__init__()
        self.names = names

    def filter(self, df:Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
        """ Default pass-through implementation"""
        if df is None:
            return None
        elif self.names is None:
            return df
        else:
            columns = list(df.columns)
            assert set(self.names) <= set(columns)
            return df[self.names]

class IndexFilter:
    def __init__(self, max_samples=None, random_state=None) -> None:
        super().__init__()
        assert isinstance(max_samples, (int, float, type(None)))
        if isinstance(max_samples, float):
            assert 0.0 < max_samples <= 1.0
        elif isinstance(max_samples, int):
            assert 1 <= max_samples
        self.max_samples = max_samples
        self.random_state = random_state

    def filter(self,X:pd.DataFrame, Y:Optional[pd.DataFrame]=None
               ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        if self.max_samples is None:
            return (X,Y)
        elif isinstance(self.max_samples, float):
            if self.max_samples == 1.0: return (X,Y)
            n_samples = max( 1 , int(len(X)*self.max_samples) )
        else:
            if (self.max_samples >= len(X)): return (X,Y)
            n_samples = min( self.max_samples , len(X) )

        X_samples = X
        Y_samples = Y

        splitter = AdaptiveShuffleSplit(
            train_size=n_samples, random_state=self.random_state)
        for (samples_idx,_) in splitter.split(X, Y):
            X_samples = X.iloc[samples_idx]
            Y_samples = None if (Y is None) else Y.iloc[samples_idx]
            break

        return (X_samples, Y_samples)
