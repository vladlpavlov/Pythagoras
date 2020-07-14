
# Workaround to ensure compatibility with Python <= 3.6
# Versions 3.6 and below do not support postponed evaluation
class AbstractPredictor(LoggableObject):
    pass

class AbstractPredictor(LoggableObject):
    """A base class for loggable predictors """

    def __init__(self, *args, **kwargs) -> None:
        kwargs["reveal_calling_method"] = kwargs.get(
            "reveal_calling_method", True)
        super().__init__(*args, **kwargs)

    def fit(self
            , X: pd.DataFrame
            , y: pd.Series
            ) -> AbstractPredictor:

        if type(self) == AbstractPredictor:
            raise NotImplementedError

        X.sort_index(inplace=True)
        y.sort_index(inplace=True)
        assert (X.index == y.index).all()

        log_message = f"==> Starting fittig a model "
        log_message += "using a DataFrame named < "
        log_message += NeatStr.object_names(X, div_ch=" / ")
        log_message += f" > with the shape {X.shape}, and a Series named < "
        log_message += NeatStr.object_names(y, div_ch=" / ") + " >."
        self.info(log_message)

    def predict(self
                , X: pd.DataFrame
                ) -> pd.Series:

        if type(self) == AbstractPredictor:
            raise NotImplementedError

        assert self.is_fitted

        log_message = f"==> Starting generating predictions "
        log_message += "using a DataFrame named < "
        log_message += NeatStr.object_names(X, div_ch=" / ")
        log_message += f" > with the shape {X.shape}."
        self.info(log_message)

    @property
    def is_fitted(self) -> bool:
        raise NotImplementedError
