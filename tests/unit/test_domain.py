import pytest
from pydantic import ValidationError

from vehicle_price.domain import ContractError, Feature, Metadata, Vehicle


def test_valid_vehicle():
    v = Vehicle(
        marque="bmw",
        date_first_circulation="2018-03-01",
        km=108946,
        gearbox="auto",
    )
    assert v.marque == "bmw"
    assert v.km == 108946


def test_negative_km_rejected():
    with pytest.raises(ValidationError):
        Vehicle(
            marque="bmw",
            date_first_circulation="2018-03-01",
            km=-1,
            gearbox="auto",
        )


def test_future_date_rejected():
    with pytest.raises(ValidationError):
        Vehicle(
            marque="bmw",
            date_first_circulation="2099-01-01",
            km=10000,
            gearbox="auto",
        )


def _metadata() -> Metadata:
    return Metadata(
        model_version="1.0.0",
        features={
            "marque": Feature(
                type="categorical", allowed_values=["audi", "bmw", "ford", "tesla"]
            ),
            "gearbox": Feature(type="categorical", allowed_values=["manual", "auto"]),
        },
    )


def test_invalid_brand_raises_contract_error():
    vehicle = Vehicle(
        marque="peugeot",
        date_first_circulation="2018-03-01",
        km=108946,
        gearbox="auto",
    )
    with pytest.raises(ContractError):
        _metadata().validate_vehicle(vehicle)


@pytest.mark.parametrize(
    "metadata",
    [
        {"model_version": "", "features": {}},
        {
            "model_version": "1.0.0",
            "features": {
                "gearbox": {"type": "categorical", "allowed_values": ["auto"]}
            },
        },
        {
            "model_version": "1.0.0",
            "features": {
                "marque": {"type": "categorical", "allowed_values": ["bmw"]},
                "gearbox": {"type": "categorical", "allowed_values": []},
            },
        },
    ],
    ids=["empty_version", "missing_marque", "empty_gearbox_values"],
)
def test_incomplete_metadata_rejected(metadata):
    with pytest.raises(ValidationError):
        Metadata.model_validate(metadata)


def test_invalid_gearbox_raises_contract_error():
    vehicle = Vehicle(
        marque="bmw",
        date_first_circulation="2018-03-01",
        km=108946,
        gearbox="cvt",
    )
    with pytest.raises(ContractError):
        _metadata().validate_vehicle(vehicle)
