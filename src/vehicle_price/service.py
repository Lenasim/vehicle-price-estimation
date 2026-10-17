from threading import BoundedSemaphore

from vehicle_price.domain import BusyError, Metadata, Prediction, Predictor, Vehicle


class PredictionService:
    """Coordinate contract validation, capacity control, and prediction."""

    def __init__(self, predictor: Predictor, metadata: Metadata, concurrency: int):
        """Configure prediction dependencies and the concurrency limit."""
        self.predictor = predictor
        self.metadata = metadata
        self.slots = BoundedSemaphore(concurrency)

    def predict(self, vehicle: Vehicle) -> Prediction:
        """Validate a vehicle and produce a versioned price prediction."""
        self.metadata.validate_vehicle(vehicle)
        if not self.slots.acquire(blocking=False):
            raise BusyError("Inference capacity exhausted")
        try:
            price = self.predictor.predict(vehicle)
            return Prediction(
                predicted_price=price,
                model_version=self.metadata.model_version,
            )
        finally:
            self.slots.release()
