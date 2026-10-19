import numpy as np
import pytest

from vehicle_price.adapters import JoblibPredictor
from vehicle_price.domain import Vehicle


class StubPipeline:
    def __init__(self, output):
        self.output = np.array(output)
        self.received = None

    def predict(self, df):
        self.received = df
        return self.output


@pytest.fixture
def vehicle():
    return Vehicle(
        marque="bmw",
        date_first_circulation="2018-03-01",
        km=108946,
        gearbox="auto",
    )


def test_predictor_builds_single_row_model_input(vehicle):
    pipeline = StubPipeline([1234.5])

    price = JoblibPredictor(pipeline).predict(vehicle)

    assert price == 1234.5
    assert pipeline.received.to_dict("records") == [
        {
            "marque": "bmw",
            "date_first_circulation": "2018-03-01",
            "km": 108946.0,
            "gearbox": "auto",
        }
    ]


@pytest.mark.parametrize(
    "output",
    [[float("nan")], [float("inf")], [-1.0], [1.0, 2.0], []],
    ids=["nan", "inf", "negative", "two_rows", "empty"],
)
def test_predictor_rejects_invalid_model_output(vehicle, output):
    with pytest.raises(RuntimeError):
        JoblibPredictor(StubPipeline(output)).predict(vehicle)
