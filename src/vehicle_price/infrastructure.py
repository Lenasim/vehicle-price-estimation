import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

from vehicle_price.domain import Metadata


class AgeFromCirculationDate(BaseEstimator, TransformerMixin):
    """Reproduce the notebook transformer required by the model artifact."""

    def __init__(
        self,
        date_column: str = "date_first_circulation",
        age_column: str = "age_years",
    ):
        """Configure the source date column and generated age column."""
        self.date_column = date_column
        self.age_column = age_column

    def fit(self, X: pd.DataFrame, y=None):
        """Return this stateless transformer without learning parameters."""
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Replace the circulation date with vehicle age in years."""
        X = X.copy()
        reference_date = pd.Timestamp.now().normalize()
        dates = pd.to_datetime(X[self.date_column])
        X[self.age_column] = (reference_date - dates).dt.days / 365.25
        return X.drop(columns=[self.date_column])


def load_metadata(path: Path) -> Metadata:
    """Read and validate model metadata from a JSON file."""
    return Metadata.model_validate(json.loads(path.read_text()))


def load_pipeline(path: Path) -> Pipeline:
    """Load a pipeline while resolving its notebook-defined class reference."""
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
