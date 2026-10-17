from datetime import date
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Feature(BaseModel):
    """Describe one model feature and its optional accepted values."""

    type: str
    allowed_values: list[str] | None = None


class Metadata(BaseModel):
    """Represent the model version and its input contract."""

    model_version: str
    features: dict[str, Feature]

    @model_validator(mode="after")
    def check_contract(self) -> "Metadata":
        """Reject incomplete metadata required for categorical validation."""
        if not self.model_version:
            raise ValueError("model_version must not be empty")
        for field in ("marque", "gearbox"):
            if not self.features.get(field) or not self.features[field].allowed_values:
                raise ValueError(f"Missing allowed_values for {field}")
        return self

    def validate_vehicle(self, vehicle: "Vehicle") -> None:
        """Reject vehicle categories unsupported by the loaded model."""
        for field in ("marque", "gearbox"):
            allowed = self.features[field].allowed_values
            if getattr(vehicle, field) not in allowed:
                raise ContractError(f"Unsupported {field}: {getattr(vehicle, field)}")


class Vehicle(BaseModel):
    """Validated vehicle attributes accepted by the inference API."""

    model_config = ConfigDict(extra="forbid")
    marque: str = Field(
        min_length=1,
        max_length=100,
        description="Brand accepted by the loaded model metadata.",
        examples=["bmw"],
    )
    date_first_circulation: date = Field(
        description="First registration date; future dates are rejected.",
        examples=["2018-03-01"],
    )
    km: float = Field(
        ge=0,
        allow_inf_nan=False,
        description="Non-negative odometer reading in kilometres.",
        examples=[108946],
    )
    gearbox: str = Field(
        min_length=1,
        max_length=100,
        description="Gearbox accepted by the loaded model metadata.",
        examples=["auto"],
    )

    @field_validator("km", mode="before")
    @classmethod
    def numeric_km(cls, value):
        """Require mileage to be a JSON number rather than a coerced value."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("km must be a JSON number")  # noqa: TRY004 (pydantic requires ValueError)
        return value

    @field_validator("date_first_circulation")
    @classmethod
    def past_date(cls, value: date) -> date:
        """Reject circulation dates later than today."""
        if value > date.today():
            raise ValueError("date cannot be in the future")
        return value


class Prediction(BaseModel):
    """Successful prediction and the model version that produced it."""

    predicted_price: float = Field(
        description="Finite, non-negative model output without display rounding.",
        examples=[7129.82666015625],
    )
    model_version: str = Field(
        description="Version from model metadata.", examples=["1.0.0"]
    )


class HealthResponse(BaseModel):
    """Readiness state for a worker with a loaded model."""

    status: Literal["ok"] = "ok"
    model_version: str = Field(
        description="Version of the loaded model.", examples=["1.0.0"]
    )


class ErrorDetail(BaseModel):
    """Stable machine-readable error details."""

    code: str = Field(examples=["invalid_request"])
    message: str = Field(examples=["Request schema validation failed"])
    request_id: str | None = Field(
        description="Correlation ID also returned in the X-Request-ID header.",
        examples=["5a5e38e2-b76f-41ad-9954-4a9f874a7f50"],
    )


class ErrorResponse(BaseModel):
    """Public error envelope; internal exception details are never returned."""

    error: ErrorDetail


class Predictor(Protocol):
    def predict(self, vehicle: Vehicle) -> float:
        """Return a price estimate for a validated vehicle."""
        ...


class ContractError(ValueError):
    pass


class BusyError(RuntimeError):
    pass
