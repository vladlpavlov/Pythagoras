import pandas as pd
from Pythagoras.util import *
from Pythagoras.logging import *


class AbstractFeatureMaker(LoggableObject):
    """An base class for transformers that create new features"""

    def __init__(self,  *args, **kwargs) -> None:
        kwargs["reveal_calling_method"] = kwargs.get(
            "reveal_calling_method", True)
        super().__init__(*args, **kwargs)

    def fit_transform(self
            ,X:pd.core.frame.DataFrame
            ,y=None
            ) -> pd.core.frame.DataFrame:
        raise NotImplementedError

    def transform(self
            ,X:pd.core.frame.DataFrame
            ) -> pd.core.frame.DataFrame:
        raise NotImplementedError