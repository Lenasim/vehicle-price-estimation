from vehicle_price.domain import Feature, Metadata, Vehicle
from vehicle_price.service import PredictionService


class StubPredictor:
    def predict(self, vehicle: Vehicle) -> float:
        return 1234.56789


def test_prediction_preserves_model_precision():
    metadata = Metadata(
        model_version="1.0.0",
        features={
            "marque": Feature(type="categorical", allowed_values=["bmw"]),
            "gearbox": Feature(type="categorical", allowed_values=["auto"]),
        },
    )
    service = PredictionService(StubPredictor(), metadata, concurrency=1)
    vehicle = Vehicle(
        marque="bmw",
        date_first_circulation="2018-03-01",
        km=108946,
        gearbox="auto",
    )

    prediction = service.predict(vehicle)

    assert prediction.predicted_price == 1234.56789
    assert prediction.model_version == "1.0.0"
