"""Load the supplied pipeline with its notebook-defined transformer."""

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline


class AgeFromCirculationDate(BaseEstimator, TransformerMixin):
    """Derive vehicle age using the transformer's behavior in the training notebook."""

    def __init__(
        self,
        date_column: str = "date_first_circulation",
        age_column: str = "age_years",
    ):
        self.date_column = date_column
        self.age_column = age_column

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        reference_date = pd.Timestamp.now().normalize()
        dates = pd.to_datetime(X[self.date_column])
        X[self.age_column] = (reference_date - dates).dt.days / 365.25
        return X.drop(columns=[self.date_column])


def load_pipeline(path: str | Path) -> Pipeline:
    """Resolve the artifact's ``__main__`` class reference while unpickling."""
    main_module = sys.modules["__main__"]
    missing = object()
    previous = getattr(main_module, "AgeFromCirculationDate", missing)
    main_module.AgeFromCirculationDate = AgeFromCirculationDate
    try:
        return joblib.load(path)
    finally:
        if previous is missing:
            del main_module.AgeFromCirculationDate
        else:
            main_module.AgeFromCirculationDate = previous
