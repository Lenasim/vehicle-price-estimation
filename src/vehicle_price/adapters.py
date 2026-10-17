import math

import pandas as pd
from sklearn.pipeline import Pipeline

from vehicle_price.domain import Vehicle


class JoblibPredictor:
    """Adapt a scikit-learn pipeline to the domain predictor port."""

    def __init__(self, pipeline: Pipeline):
        """Store the already-loaded pipeline used for inference."""
        self.pipeline = pipeline

    def predict(self, vehicle: Vehicle) -> float:
        """Convert a vehicle to model input and return a valid price."""
        df = pd.DataFrame(
            [
                {
                    "marque": vehicle.marque,
                    "date_first_circulation": str(vehicle.date_first_circulation),
                    "km": vehicle.km,
                    "gearbox": vehicle.gearbox,
                }
            ]
        )
        predictions = self.pipeline.predict(df)
        if len(predictions) != 1:
            raise RuntimeError("Model must return one prediction")
        result = float(predictions[0])
        if not math.isfinite(result) or result < 0:
            raise RuntimeError("Model returned an invalid price")
        return result
